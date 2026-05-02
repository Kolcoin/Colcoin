from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from .app import DEFAULT_DATA_FILE, serve
from .crawler import SEOAuditor
from .models import Project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Automated white-hat SEO promotion service")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Run the web service")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8080)
    serve_parser.add_argument("--data-file", type=Path, default=DEFAULT_DATA_FILE)
    serve_parser.add_argument("--max-pages", type=int, default=25)

    audit_parser = subparsers.add_parser("audit", help="Run a one-off website audit")
    audit_parser.add_argument("site_url")
    audit_parser.add_argument("--name", default="CLI project")
    audit_parser.add_argument("--keyword", action="append", default=[])
    audit_parser.add_argument("--max-pages", type=int, default=25)
    audit_parser.add_argument("--output", type=Path)

    args = parser.parse_args(argv)
    command = args.command or "serve"
    if command == "serve":
        serve(args.host, args.port, args.data_file, args.max_pages)
        return 0

    project = Project(
        id=uuid.uuid4().hex[:10],
        name=args.name,
        site_url=args.site_url,
        keywords=args.keyword,
    )
    report = SEOAuditor(max_pages=args.max_pages).audit(project).to_dict()
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
