from __future__ import annotations

import re
import time
from html.parser import HTMLParser
from urllib.parse import quote, urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

from .models import AuditReport, PageAudit, Project, utc_now_iso

USER_AGENT = "SeoGrowthBot/1.0 (+https://example.com/seo-automation)"
WORD_RE = re.compile(r"[\wА-Яа-яЁё-]+", re.UNICODE)


class SeoHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.h1: list[str] = []
        self.h2: list[str] = []
        self.canonical = ""
        self.links: list[str] = []
        self.missing_alt_images = 0
        self._tag_stack: list[str] = []
        self._text_by_tag: dict[str, list[str]] = {"title": [], "h1": [], "h2": []}
        self.visible_text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name.lower(): value or "" for name, value in attrs}
        self._tag_stack.append(tag)
        if tag == "meta" and attr_map.get("name", "").lower() == "description":
            self.meta_description = attr_map.get("content", "").strip()
        elif tag == "link" and attr_map.get("rel", "").lower() == "canonical":
            self.canonical = attr_map.get("href", "").strip()
        elif tag == "a" and attr_map.get("href"):
            self.links.append(attr_map["href"])
        elif tag == "img" and not attr_map.get("alt", "").strip():
            self.missing_alt_images += 1

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._tag_stack) - 1, -1, -1):
            if self._tag_stack[index] == tag:
                del self._tag_stack[index:]
                break
        if tag == "title":
            self.title = " ".join(self._text_by_tag["title"]).strip()
        elif tag == "h1":
            text = " ".join(self._text_by_tag["h1"]).strip()
            if text:
                self.h1.append(text)
            self._text_by_tag["h1"].clear()
        elif tag == "h2":
            text = " ".join(self._text_by_tag["h2"]).strip()
            if text:
                self.h2.append(text)
            self._text_by_tag["h2"].clear()

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        current_tag = self._tag_stack[-1] if self._tag_stack else ""
        if current_tag in self._text_by_tag:
            self._text_by_tag[current_tag].append(text)
        if current_tag not in {"script", "style", "noscript"}:
            self.visible_text_parts.append(text)

    @property
    def visible_text(self) -> str:
        return " ".join(self.visible_text_parts)


class SeoCrawler:
    def __init__(self, site_url: str, keywords: list[str], max_pages: int = 20, delay_seconds: float = 0.1) -> None:
        self.site_url = normalize_url(site_url)
        self.keywords = [keyword.strip() for keyword in keywords if keyword.strip()]
        self.max_pages = max_pages
        self.delay_seconds = delay_seconds
        self._domain = urlparse(self.site_url).netloc
        self._robots = self._load_robots()

    def crawl(self) -> list[PageAudit]:
        queue = [self.site_url]
        seen: set[str] = set()
        audits: list[PageAudit] = []

        while queue and len(audits) < self.max_pages:
            url = queue.pop(0)
            if url in seen or not self._is_internal(url):
                continue
            seen.add(url)
            if not self._robots.can_fetch(USER_AGENT, url):
                audits.append(PageAudit(url=url, status_code=999, issues=["Blocked by robots.txt"]))
                continue

            audit = self._audit_page(url)
            audits.append(audit)
            for link in audit.internal_links:
                if link not in seen and link not in queue and len(seen) + len(queue) < self.max_pages:
                    queue.append(link)
            time.sleep(self.delay_seconds)

        return audits

    def _audit_page(self, url: str) -> PageAudit:
        started = time.monotonic()
        try:
            response = urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=10)
            status_code = int(getattr(response, "status", 200))
            content_type = response.headers.get("content-type", "")
            body = response.read(1_500_000)
        except Exception as exc:  # noqa: BLE001 - surfaced in the audit report.
            return PageAudit(url=url, status_code=0, issues=[f"Не удалось загрузить страницу: {exc}"])

        load_time_ms = int((time.monotonic() - started) * 1000)
        if "html" not in content_type:
            return PageAudit(url=url, status_code=status_code, load_time_ms=load_time_ms, issues=["Страница не является HTML"])

        html = body.decode("utf-8", errors="replace")
        parser = SeoHtmlParser()
        parser.feed(html)

        internal_links, external_links = split_links(url, parser.links, self._domain)
        text = parser.visible_text.lower()
        keywords_found = {keyword: text.count(keyword.lower()) for keyword in self.keywords}
        audit = PageAudit(
            url=url,
            status_code=status_code,
            title=parser.title,
            meta_description=parser.meta_description,
            h1=parser.h1,
            h2=parser.h2,
            canonical=urljoin(url, parser.canonical) if parser.canonical else "",
            word_count=len(WORD_RE.findall(parser.visible_text)),
            internal_links=internal_links,
            external_links=external_links,
            missing_alt_images=parser.missing_alt_images,
            keywords_found=keywords_found,
            load_time_ms=load_time_ms,
        )
        audit.issues, audit.recommendations = inspect_page(audit, self.keywords)
        return audit

    def _load_robots(self) -> RobotFileParser:
        robots = RobotFileParser()
        robots_url = urljoin(self.site_url, "/robots.txt")
        robots.set_url(robots_url)
        try:
            robots.read()
        except Exception:
            robots.parse("")
        return robots

    def _is_internal(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and parsed.netloc == self._domain


def normalize_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    path = parsed.path or "/"
    netloc = parsed.netloc
    if parsed.hostname:
        host = parsed.hostname.encode("idna").decode("ascii")
        if parsed.port:
            host = f"{host}:{parsed.port}"
        netloc = host
    return parsed._replace(
        netloc=netloc,
        path=quote(path, safe="/%"),
        query=quote(parsed.query, safe="=&;%+"),
        fragment="",
    ).geturl()


def split_links(base_url: str, raw_links: list[str], domain: str) -> tuple[list[str], list[str]]:
    internal: list[str] = []
    external: list[str] = []
    for raw_link in raw_links:
        absolute, _fragment = urldefrag(urljoin(base_url, raw_link))
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        normalized = normalize_url(parsed._replace(fragment="", query="").geturl())
        target = internal if parsed.netloc == domain else external
        if normalized not in target:
            target.append(normalized)
    return internal, external


def inspect_page(page: PageAudit, keywords: list[str]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    recommendations: list[str] = []
    if page.status_code >= 400 or page.status_code == 0:
        issues.append("Страница недоступна")
        recommendations.append("Сначала исправьте ошибку загрузки страницы.")
    if not page.title:
        issues.append("Не заполнен title")
        recommendations.append("Добавьте уникальный title с основным запросом ближе к началу.")
    elif len(page.title) > 70:
        issues.append("Title слишком длинный")
        recommendations.append("Сократите title примерно до 50-70 символов.")
    if not page.meta_description:
        issues.append("Не заполнен meta description")
        recommendations.append("Добавьте понятное meta description для поискового сниппета.")
    if len(page.h1) != 1:
        issues.append("На странице должен быть ровно один H1")
        recommendations.append("Оставьте один понятный H1, соответствующий смыслу страницы.")
    if page.word_count < 250:
        issues.append("Мало полезного текста")
        recommendations.append("Расширьте страницу: добавьте ответы, примеры, цены, FAQ и доказательства.")
    if page.missing_alt_images:
        issues.append("У изображений нет alt-текста")
        recommendations.append("Добавьте описательные alt-атрибуты к важным изображениям.")
    missing_keywords = [keyword for keyword in keywords if page.keywords_found.get(keyword, 0) == 0]
    if missing_keywords:
        issues.append("Целевые запросы отсутствуют в видимом тексте")
        recommendations.append("Естественно раскройте недостающие запросы: " + ", ".join(missing_keywords[:5]))
    return issues, dedupe(recommendations)


def dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


class SEOAuditor:
    def __init__(self, max_pages: int = 25) -> None:
        self.max_pages = max_pages

    def audit(self, project: Project) -> AuditReport:
        crawler = SeoCrawler(project.site_url, project.keywords, max_pages=self.max_pages)
        pages = crawler.crawl()
        return AuditReport(
            project_id=project.id,
            site_url=project.site_url,
            generated_at=utc_now_iso(),
            pages=pages,
            action_plan=build_action_plan(pages),
        )


def build_action_plan(pages: list[PageAudit]) -> list[str]:
    actions: list[str] = []
    for page in sorted(pages, key=lambda item: item.score):
        for recommendation in page.recommendations:
            actions.append(f"{page.url}: {recommendation}")
    if not actions:
        actions.append("Продолжайте публиковать полезный контент и проверяйте позиции каждую неделю.")
    return dedupe(actions)[:20]
