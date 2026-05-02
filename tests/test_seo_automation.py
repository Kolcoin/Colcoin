import json

from seo_automation.audit import run_seo_audit
from seo_automation.models import CrawlResult, PageData
from seo_automation.planner import build_keyword_action_plan


def _page(url: str, title: str, description: str, h1: list[str], words: int) -> PageData:
    return PageData(
        url=url,
        final_url=url,
        status_code=200,
        content_type="text/html",
        title=title,
        description=description,
        h1=h1,
        canonical=url,
        robots="",
        word_count=words,
        out_links=[],
        error="",
    )


def test_audit_detects_basic_issues() -> None:
    crawl = CrawlResult(
        start_url="https://example.com",
        pages=[
            _page("https://example.com", "", "", [], 100),
            _page(
                "https://example.com/service",
                "Service page",
                "A" * 171,
                ["One", "Two"],
                900,
            ),
        ],
    )

    result = run_seo_audit(crawl)
    assert result["total_pages"] == 2
    first_codes = {issue["code"] for issue in result["pages"][0]["issues"]}
    second_codes = {issue["code"] for issue in result["pages"][1]["issues"]}
    assert "missing_title" in first_codes
    assert "missing_description" in first_codes
    assert "missing_h1" in first_codes
    assert "thin_content" in first_codes
    assert "description_too_long" in second_codes
    assert "multiple_h1" in second_codes
    assert "title_too_short" in second_codes


def test_planner_suggests_target_pages() -> None:
    crawl = CrawlResult(
        start_url="https://example.com",
        pages=[
            _page(
                "https://example.com/windows",
                "Пластиковые окна в Москве",
                "Установка пластиковых окон под ключ.",
                ["Пластиковые окна"],
                420,
            ),
            _page(
                "https://example.com/doors",
                "Металлические двери",
                "Входные и межкомнатные двери.",
                ["Металлические двери"],
                390,
            ),
        ],
    )

    plan = build_keyword_action_plan(crawl, ["пластиковые окна", "монтаж дверей"])
    assert len(plan) == 2
    assert plan[0].target_url == "https://example.com/windows"
    assert plan[0].action == "Optimize existing page"
    assert plan[1].action in {"Create dedicated landing page", "Optimize existing page"}

    as_json = json.dumps([item.to_dict() for item in plan], ensure_ascii=False)
    assert "пластиковые окна" in as_json
