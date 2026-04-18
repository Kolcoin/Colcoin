"""CLI entrypoint for daily Telegram autoposter."""

from __future__ import annotations

import argparse
import asyncio

from .moderation import run_moderation_worker
from .runner import run_daily_post


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and publish Telegram channel post")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate a post and print it without publishing to Telegram",
    )
    parser.add_argument(
        "--moderation-worker",
        action="store_true",
        help="Run moderation update worker (approve/reject callbacks)",
    )
    return parser


async def run_once(*, dry_run: bool = False) -> str:
    """Single-run helper used by scripts and tests."""
    return await run_daily_post(dry_run=dry_run)


def main() -> None:
    args = build_parser().parse_args()
    if args.moderation_worker:
        asyncio.run(run_moderation_worker())
        return
    asyncio.run(run_once(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
