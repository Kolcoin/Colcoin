from __future__ import annotations

import re
from collections.abc import Iterable

from .models import CrawlResult, PlanItem


def _tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Zа-яА-Я0-9]+", value.lower()) if token}


def _page_signature(title: str, description: str, url: str) -> set[str]:
    return _tokenize(" ".join([title, description, url]))


def build_keyword_action_plan(crawl: CrawlResult, keywords: Iterable[str]) -> list[PlanItem]:
    pages = []
    for page in crawl.pages:
        if page.error or page.status_code >= 400:
            continue
        pages.append((page, _page_signature(page.title, page.description, page.url)))

    plan: list[PlanItem] = []
    for keyword in keywords:
        normalized = keyword.strip()
        if not normalized:
            continue

        keyword_tokens = _tokenize(normalized)
        best_page = None
        best_score = 0.0
        for page, signature in pages:
            if not signature:
                continue
            overlap = len(keyword_tokens.intersection(signature))
            if overlap == 0:
                continue
            score = overlap / max(1, len(keyword_tokens))
            if score > best_score:
                best_page = page
                best_score = score

        if best_page is None:
            plan.append(
                PlanItem(
                    keyword=normalized,
                    target_url="(new page required)",
                    action="Create dedicated landing page",
                    reason="No crawled page contains key terms from this query.",
                    relevance=0.0,
                    next_steps=[
                        "Draft page structure with H1 + supporting H2 sections.",
                        "Add concise title (<= 65 chars) and description (<= 160 chars).",
                        "Link this new page from a relevant existing page.",
                    ],
                )
            )
            continue

        next_steps: list[str] = []
        if len(best_page.title) < 10:
            next_steps.append("Rewrite title to include the keyword naturally.")
        if len(best_page.description) < 50:
            next_steps.append("Expand meta description with value proposition and CTA.")
        if not best_page.h1:
            next_steps.append("Add one clear H1 containing the main term.")
        if best_page.word_count < 300:
            next_steps.append("Increase on-page content depth to at least 300 words.")
        if not next_steps:
            next_steps.append("Track rankings weekly and iterate based on impressions/clicks.")

        plan.append(
            PlanItem(
                keyword=normalized,
                target_url=best_page.url,
                action="Optimize existing page",
                reason="Most relevant page by keyword overlap with title/description/url.",
                relevance=round(best_score, 2),
                next_steps=next_steps,
            )
        )

    return sorted(plan, key=lambda item: item.relevance, reverse=True)
