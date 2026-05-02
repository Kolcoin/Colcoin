from __future__ import annotations

from collections import deque
from html.parser import HTMLParser
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

from .models import CrawlResult, PageData


def _normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    return urlunparse((scheme, netloc, path, "", parsed.query, ""))


def _tokenize_text(value: str) -> list[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in value)
    return [token for token in cleaned.split() if token]


class _SEOHTMLParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.h1: list[str] = []
        self.links: list[str] = []
        self._text_nodes: list[str] = []
        self._inside_title = False
        self._inside_h1 = False
        self._title_buffer: list[str] = []
        self._h1_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()

        if tag == "title":
            self._inside_title = True
            self._title_buffer = []
            return

        if tag == "h1":
            self._inside_h1 = True
            self._h1_buffer = []
            return

        if tag == "meta":
            name = attr_map.get("name", "").lower()
            content = attr_map.get("content", "").strip()
            if name == "description" and content:
                self.description = content
            if name == "robots" and content:
                self.robots = content
            return

        if tag == "link":
            rel = attr_map.get("rel", "").lower()
            href = attr_map.get("href", "").strip()
            if "canonical" in rel and href:
                self.canonical = _normalize_url(urljoin(self.base_url, href))
            return

        if tag == "a":
            href = attr_map.get("href", "").strip()
            if not href or href.startswith("#"):
                return
            absolute_url = _normalize_url(urljoin(self.base_url, href))
            parsed = urlparse(absolute_url)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                self.links.append(absolute_url)

    def handle_data(self, data: str) -> None:
        stripped = data.strip()
        if not stripped:
            return
        self._text_nodes.append(stripped)
        if self._inside_title:
            self._title_buffer.append(stripped)
        if self._inside_h1:
            self._h1_buffer.append(stripped)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._inside_title = False
            self.title = " ".join(self._title_buffer).strip()
            return
        if tag == "h1":
            self._inside_h1 = False
            value = " ".join(self._h1_buffer).strip()
            if value:
                self.h1.append(value)
            return

    @property
    def word_count(self) -> int:
        joined = " ".join(self._text_nodes)
        return len(_tokenize_text(joined))


def parse_html_document(html: str, base_url: str) -> dict[str, object]:
    parser = _SEOHTMLParser(base_url=base_url)
    parser.feed(html)
    parser.close()
    return {
        "title": parser.title,
        "description": parser.description,
        "canonical": parser.canonical,
        "robots": parser.robots,
        "h1": parser.h1,
        "links": parser.links,
        "word_count": parser.word_count,
    }


class SiteCrawler:
    def __init__(
        self,
        start_url: str,
        max_pages: int = 50,
        timeout_seconds: int = 15,
        same_domain_only: bool = True,
    ) -> None:
        self.start_url = _normalize_url(start_url)
        self.max_pages = max_pages
        self.timeout_seconds = timeout_seconds
        self.same_domain_only = same_domain_only
        self._start_netloc = urlparse(self.start_url).netloc

    def crawl(self) -> CrawlResult:
        queue: deque[str] = deque([self.start_url])
        visited: set[str] = set()
        pages: list[PageData] = []

        while queue and len(visited) < self.max_pages:
            url = queue.popleft()
            if url in visited:
                continue
            visited.add(url)
            page = self._fetch_page(url)
            pages.append(page)

            for out_link in self._filter_links(page.out_links):
                if out_link not in visited:
                    queue.append(out_link)

        return CrawlResult(start_url=self.start_url, pages=pages)

    def _filter_links(self, links: Iterable[str]) -> list[str]:
        if not self.same_domain_only:
            return list(links)
        return [link for link in links if urlparse(link).netloc == self._start_netloc]

    def _fetch_page(self, url: str) -> PageData:
        request = Request(
            url=url,
            headers={
                "User-Agent": (
                    "SEOAutomationBot/1.0 (+https://example.com/"
                    " safe-seo-audit-crawler)"
                )
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                status_code = int(response.getcode() or 0)
                final_url = _normalize_url(response.geturl())
                content_type = response.headers.get("Content-Type", "")
                raw = response.read()
                encoding = response.headers.get_content_charset() or "utf-8"
                html = raw.decode(encoding, errors="replace")
                page = PageData(
                    url=url,
                    final_url=final_url,
                    status_code=status_code,
                    content_type=content_type,
                )
                if "text/html" in content_type.lower():
                    parsed = parse_html_document(html, base_url=final_url)
                    page.title = str(parsed["title"])
                    page.description = str(parsed["description"])
                    page.h1 = [str(item) for item in parsed["h1"]]
                    page.canonical = str(parsed["canonical"])
                    page.robots = str(parsed["robots"])
                    page.word_count = int(parsed["word_count"])
                    page.out_links = [str(item) for item in parsed["links"]]
                return page
        except HTTPError as exc:
            return PageData(
                url=url,
                final_url=url,
                status_code=exc.code,
                content_type="",
                error=f"HTTPError: {exc.reason}",
            )
        except URLError as exc:
            return PageData(
                url=url,
                final_url=url,
                status_code=0,
                content_type="",
                error=f"URLError: {exc.reason}",
            )
        except Exception as exc:  # pragma: no cover
            return PageData(
                url=url,
                final_url=url,
                status_code=0,
                content_type="",
                error=f"{exc.__class__.__name__}: {exc}",
            )


PageSnapshot = PageData
