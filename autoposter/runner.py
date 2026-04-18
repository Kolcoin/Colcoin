"""Daily post runner orchestration."""

from __future__ import annotations

import random

from .config import load_autoposter_config
from .generator import generate_post
from .moderation import send_for_moderation
from .state import StateStore
from .telegram_publisher import TelegramPublisher


def choose_topic(topics: list[str], recent: list[str]) -> str:
    """Pick topic different from recent ones when possible."""
    if not topics:
        raise ValueError("topics list is empty")
    normalized_recent = [item.strip() for item in recent if item.strip()]
    options = [topic for topic in topics if topic not in normalized_recent]
    return random.choice(options or topics)


async def run_daily_post(*, dry_run: bool = False) -> str:
    """Generate one post and publish it unless dry-run is enabled."""
    config = load_autoposter_config()
    state = StateStore(config.state_file)
    recent_topics = state.recent_topics(limit=2)
    topic = choose_topic(config.topics, recent_topics)

    post = await generate_post(config=config, topic=topic)

    if dry_run:
        print("=== DRY RUN ===")
        print(post)
        return post

    if config.moderation_enabled:
        token = await send_for_moderation(
            config=config,
            state=state,
            topic=topic,
            post_text=post,
        )
        print(f"Moderation draft sent to {config.moderation_chat_id} (token={token})")
        return post

    publisher = TelegramPublisher(config)
    await publisher.publish_text(post)
    state.append(topic, post)
    return post
