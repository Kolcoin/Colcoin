#!/usr/bin/env python3
"""
Blog content pipeline:
topics CSV -> HTML pages -> REALTY_BLOG_POSTS -> sitemap.xml
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REALTY_DATA_PATH = ROOT / "realty-data.js"
SITEMAP_PATH = ROOT / "sitemap.xml"
DEFAULT_DOMAIN = "https://xn--h1aagfvid9b.xn--p1ai"


@dataclass
class Topic:
    slug: str
    title: str
    category: str
    excerpt: str
    date: str
    keywords: str
    target_dir: str
    priority: str
    changefreq: str

    @property
    def relative_url(self) -> str:
        target = self.target_dir.strip("/")
        if target:
            return f"./{target}/{self.slug}.html"
        return f"./{self.slug}.html"

    def absolute_url(self, domain: str) -> str:
        root = domain.rstrip("/")
        target = self.target_dir.strip("/")
        if target:
            return f"{root}/{target}/{self.slug}.html"
        return f"{root}/{self.slug}.html"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate blog pages and auto-update blog index + sitemap."
    )
    parser.add_argument(
        "--csv",
        "--topics",
        dest="csv",
        default=str(ROOT / "blog-pipeline" / "topics.csv"),
        help="Path to topics CSV.",
    )
    parser.add_argument(
        "--domain",
        "--base-url",
        dest="domain",
        default=DEFAULT_DOMAIN,
        help="Canonical domain for sitemap/canonical URLs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned changes without writing files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing generated HTML pages.",
    )
    return parser.parse_args()


def is_enabled(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def clean_date(raw: str) -> str:
    value = (raw or "").strip()
    if value:
        return value
    return dt.date.today().isoformat()


def read_topics(csv_path: Path) -> list[Topic]:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    topics: list[Topic] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"slug", "title", "category", "excerpt"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        for row in reader:
            if "enabled" in row and not is_enabled(row.get("enabled", "")):
                continue

            slug = (row.get("slug") or "").strip()
            title = (row.get("title") or "").strip()
            category = (row.get("category") or "").strip()
            excerpt = (row.get("excerpt") or "").strip()
            date = clean_date(row.get("date", ""))
            keywords = ((row.get("keywords") or row.get("focus_keyword") or "")).strip()
            target_dir = (row.get("target_dir") or "seo").strip() or "seo"
            priority = (row.get("priority") or "0.76").strip() or "0.76"
            changefreq = (row.get("changefreq") or "weekly").strip() or "weekly"

            if not slug or not title or not category or not excerpt:
                raise ValueError(
                    f"Invalid row (need slug/title/category/excerpt): {row}"
                )

            topics.append(
                Topic(
                    slug=slug,
                    title=title,
                    category=category,
                    excerpt=excerpt,
                    date=date,
                    keywords=keywords,
                    target_dir=target_dir,
                    priority=priority,
                    changefreq=changefreq,
                )
            )
    return topics


def page_html(topic: Topic, domain: str) -> str:
    title = html.escape(topic.title)
    excerpt = html.escape(topic.excerpt)
    h1 = title
    keywords = html.escape(
        topic.keywords or f"{topic.category.lower()}, новостройки москвы, новостройки мо"
    )
    canonical = topic.absolute_url(domain)
    category = html.escape(topic.category)
    date_iso = html.escape(topic.date)
    slug = html.escape(topic.slug)

    return f"""<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title} | Савушкин Эстейт</title>
    <meta name="description" content="{excerpt}" />
    <meta name="keywords" content="{keywords}" />
    <meta name="robots" content="index,follow,max-image-preview:large" />
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="ru_RU" />
    <meta property="og:site_name" content="Савушкин Эстейт" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{excerpt}" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:image" content="https://static.tildacdn.com/tild6339-3531-4536-b739-626330353335/headliner-moskva-jk-.jpg" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{excerpt}" />
    <meta name="twitter:image" content="https://static.tildacdn.com/tild6339-3531-4536-b739-626330353335/headliner-moskva-jk-.jpg" />
    <link rel="canonical" href="{canonical}" />
    <link rel="alternate" hreflang="ru-RU" href="{canonical}" />
    <link rel="alternate" hreflang="x-default" href="{canonical}" />
    <link rel="stylesheet" href="../styles.css?v=20260427-blog-pipeline-1" />
    <script type="application/ld+json">
      {{
        "@context": "https://schema.org",
        "@graph": [
          {{
            "@type": "Article",
            "headline": "{title}",
            "datePublished": "{date_iso}",
            "dateModified": "{date_iso}",
            "inLanguage": "ru-RU",
            "description": "{excerpt}",
            "url": "{canonical}",
            "author": {{
              "@type": "Organization",
              "name": "Савушкин Эстейт"
            }},
            "publisher": {{
              "@type": "Organization",
              "name": "Савушкин Эстейт"
            }}
          }},
          {{
            "@type": "BreadcrumbList",
            "itemListElement": [
              {{
                "@type": "ListItem",
                "position": 1,
                "name": "Главная",
                "item": "{domain.rstrip('/')}/"
              }},
              {{
                "@type": "ListItem",
                "position": 2,
                "name": "Блог",
                "item": "{domain.rstrip('/')}/blog.html"
              }},
              {{
                "@type": "ListItem",
                "position": 3,
                "name": "{title}",
                "item": "{canonical}"
              }}
            ]
          }}
        ]
      }}
    </script>
  </head>
  <body>
    <main class="section article-page">
      <div class="container article-container">
        <p><a class="section-link" href="../blog.html">← К блогу</a></p>
        <header class="article-hero">
          <p class="eyebrow">{category}</p>
          <h1>{h1}</h1>
          <p class="hero-text">{excerpt}</p>
          <p class="article-meta">Публикация: {date_iso}</p>
        </header>

        <section class="article-section section-muted">
          <h2>Что важно проверить перед выбором</h2>
          <ul class="article-checklist">
            <li>Сопоставьте бюджет входа и ежемесячную нагрузку с вашим сценарием покупки.</li>
            <li>Проверьте транспортную связность локации и реальные маршруты в часы пик.</li>
            <li>Сравните 3-5 альтернативных проектов по цене, срокам и рискам сделки.</li>
          </ul>
        </section>

        <section class="article-section">
          <h2>Практический разбор</h2>
          <p>
            Этот материал ({slug}) подготовлен как рабочая инструкция для принятия решения по новостройкам Москвы и МО.
            Используйте его вместе с каталогом, фильтрами по районам и ипотечным калькулятором, чтобы быстро собрать shortlist
            и перейти к безопасной сделке без лишних рисков.
          </p>
          <p>
            Если нужен персональный подбор под ваш бюджет и срок покупки — свяжитесь с экспертом:
            <a class="section-link" href="tel:+79857614885">+7 985 761-48-85</a>,
            <a class="section-link" href="https://t.me/AlexSavushkin" target="_blank" rel="noopener noreferrer">@AlexSavushkin</a>.
          </p>
        </section>

        <section class="article-section section-muted">
          <h2>Полезные ссылки</h2>
          <ul class="article-checklist">
            <li><a href="../catalog.html">Каталог новостроек Москвы и МО</a></li>
            <li><a href="../districts.html">Районы и локации</a></li>
            <li><a href="../developers.html">Застройщики</a></li>
            <li><a href="../mortgage.html">Ипотека и расчеты</a></li>
            <li><a href="../blog.html">Все статьи блога</a></li>
          </ul>
        </section>
      </div>
    </main>
  </body>
</html>
"""


def write_article_pages(
    topics: Iterable[Topic],
    domain: str,
    dry_run: bool,
    overwrite: bool,
) -> list[Topic]:
    written: list[Topic] = []
    for topic in topics:
        target_dir = ROOT / topic.target_dir.strip("/")
        file_path = target_dir / f"{topic.slug}.html"

        if file_path.exists() and not overwrite:
            print(f"skip existing: {file_path}")
            continue

        file_html = page_html(topic, domain)
        if dry_run:
            print(f"[dry-run] write page: {file_path}")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_html, encoding="utf-8")
            print(f"written page: {file_path}")
        written.append(topic)
    return written


def js_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def append_blog_posts(realty_data: Path, topics: Iterable[Topic], dry_run: bool) -> int:
    text = realty_data.read_text(encoding="utf-8")
    m = re.search(
        r"(window\.REALTY_BLOG_POSTS\s*=\s*\[)([\s\S]*?)(\n\];)",
        text,
    )
    if not m:
        raise RuntimeError("Cannot locate window.REALTY_BLOG_POSTS array in realty-data.js")

    prefix, body, suffix = m.group(1), m.group(2), m.group(3)
    existing_ids = set(re.findall(r'id:\s*"([^"]+)"', body))
    existing_urls = set(re.findall(r'url:\s*"([^"]+)"', body))

    new_blocks = []
    for topic in topics:
        post_id = topic.slug
        post_url = topic.relative_url
        if post_id in existing_ids or post_url in existing_urls:
            print(f"skip blog post (exists): {post_id} -> {post_url}")
            continue

        block = (
            "  {\n"
            f'    id: "{js_escape(post_id)}",\n'
            f'    title: "{js_escape(topic.title)}",\n'
            f'    category: "{js_escape(topic.category)}",\n'
            f'    date: "{js_escape(topic.date)}",\n'
            f'    excerpt: "{js_escape(topic.excerpt)}",\n'
            f'    url: "{js_escape(post_url)}"\n'
            "  }"
        )
        new_blocks.append(block)
        existing_ids.add(post_id)
        existing_urls.add(post_url)

    if not new_blocks:
        print("no new blog posts to append")
        return 0

    body_trimmed = body.rstrip()
    if body_trimmed and not body_trimmed.endswith(","):
        body_trimmed += ","

    joined = body_trimmed + "\n" + ",\n".join(new_blocks) + "\n"
    replacement = prefix + joined + suffix
    updated = text[: m.start()] + replacement + text[m.end() :]

    if dry_run:
        print(f"[dry-run] append {len(new_blocks)} post(s) into {realty_data}")
    else:
        realty_data.write_text(updated, encoding="utf-8")
        print(f"updated {realty_data}: +{len(new_blocks)} post(s)")
    return len(new_blocks)


def append_sitemap_urls(
    sitemap_path: Path,
    topics: Iterable[Topic],
    domain: str,
    dry_run: bool,
) -> int:
    text = sitemap_path.read_text(encoding="utf-8")
    closing = "</urlset>"
    if closing not in text:
        raise RuntimeError("sitemap.xml does not contain </urlset>")

    additions = []
    for topic in topics:
        absolute = topic.absolute_url(domain)
        loc_line = f"<loc>{absolute}</loc>"
        if loc_line in text:
            print(f"skip sitemap (exists): {absolute}")
            continue
        block = (
            "  <url>\n"
            f"    <loc>{absolute}</loc>\n"
            f"    <lastmod>{topic.date}</lastmod>\n"
            f"    <changefreq>{topic.changefreq}</changefreq>\n"
            f"    <priority>{topic.priority}</priority>\n"
            "  </url>\n"
        )
        additions.append(block)

    if not additions:
        print("no new sitemap URLs to append")
        return 0

    insertion = "".join(additions)
    updated = text.replace(closing, insertion + closing)
    if dry_run:
        print(f"[dry-run] append {len(additions)} url(s) into {sitemap_path}")
    else:
        sitemap_path.write_text(updated, encoding="utf-8")
        print(f"updated {sitemap_path}: +{len(additions)} url(s)")
    return len(additions)


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv).resolve()
    domain = args.domain.rstrip("/")
    topics = read_topics(csv_path)

    if not topics:
        print("No enabled topics in CSV. Set enabled=1 for rows you want to publish.")
        return

    print(f"topics to process: {len(topics)}")
    written_topics = write_article_pages(
        topics=topics,
        domain=domain,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
    )

    if not written_topics:
        print("No pages written. Nothing else to update.")
        return

    posts_added = append_blog_posts(
        realty_data=REALTY_DATA_PATH,
        topics=written_topics,
        dry_run=args.dry_run,
    )
    sitemap_added = append_sitemap_urls(
        sitemap_path=SITEMAP_PATH,
        topics=written_topics,
        domain=domain,
        dry_run=args.dry_run,
    )

    print("\nDone.")
    print(f"pages written: {len(written_topics)}")
    print(f"blog posts added: {posts_added}")
    print(f"sitemap urls added: {sitemap_added}")


if __name__ == "__main__":
    main()
