"""Run moderation polling worker for approve/reject actions."""

import asyncio

from autoposter.moderation import run_moderation_worker


if __name__ == "__main__":
    asyncio.run(run_moderation_worker())
