from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audit import run_seo_audit
from .crawler import SiteCrawler
from .planner import build_keyword_action_plan


def _load_keywords_file(path: Path) -> list[str]:
    rows = path.read_text(encoding="utf-8").splitlines()
    return [row.strip() for row in rows if row.strip() and not row.strip().startswith("#")]


def _load_keywords_input(raw_keywords: str | None, keywords_file: str | None) -> list[str]:
    result: list[str] = []
    if raw_keywords:
        result.extend([row.strip() for row in raw_keywords.split(",") if row.strip()])
    if keywords_file:
        result.extend(_load_keywords_file(Path(keywords_file)))
    # keep order and drop duplicates
    return list(dict.fromkeys(result))


def _add_crawl_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--url", required=True, help="Start URL, e.g. https://example.com")
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--output", help="Write full JSON report to file.")


def _run_audit(url: str, max_pages: int) -> dict[str, object]:
    crawl = SiteCrawler(start_url=url, max_pages=max_pages).crawl()
    return run_seo_audit(crawl)


def _command_audit(args: argparse.Namespace) -> int:
    audit = _run_audit(url=args.url, max_pages=args.max_pages)
    payload: dict[str, object] = {"audit": audit}

    print(f"Scanned pages: {audit['total_pages']}")
    print(f"Site score: {audit['site_score']}")
    for page in audit["pages"]:
        issues = page["issues"]
        if not issues:
            continue
        print(f"\n{page['url']} (score={page['score']})")
        for issue in issues:
            print(f"  - [{issue['level']}] {issue['code']}: {issue['message']}")

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nSaved report to {output}")
    return 0


def _command_plan(args: argparse.Namespace) -> int:
    keywords = _load_keywords_input(args.keywords, args.keywords_file)
    if not keywords:
        raise SystemExit("Provide --keywords or --keywords-file with at least one query.")
    crawl = SiteCrawler(start_url=args.url, max_pages=args.max_pages).crawl()
    plan = build_keyword_action_plan(crawl, keywords)
    payload = {"plan": [item.to_dict() for item in plan]}

    print("Keyword action plan:")
    for item in plan:
        print(f"- {item.keyword} -> {item.target_url} ({item.relevance:.2f})")
        print(f"  action: {item.action}")
        print(f"  reason: {item.reason}")
        for step in item.next_steps:
            print(f"  * {step}")

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nSaved report to {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automated safe SEO promotion assistant (crawl + audit + action plan)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Crawl and run SEO audit")
    _add_crawl_options(audit_parser)
    audit_parser.set_defaults(handler=_command_audit)

    plan_parser = subparsers.add_parser(
        "plan", help="Build keyword action plan based on crawled pages"
    )
    _add_crawl_options(plan_parser)
    plan_parser.add_argument("--keywords", help="Comma-separated keywords")
    plan_parser.add_argument("--keywords-file", help="Text file, one query per line")
    plan_parser.set_defaults(handler=_command_plan)

    args = parser.parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
