"""Storage abstractions for training-safe managed bot examples."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List


@dataclass(frozen=True)
class BotStorageEntry:
    bot_id: int
    bot_username: str
    owner_id: int
    token_encrypted: str
    created_at: datetime
    status: str = "active"
    message_count: int = 0
    last_message_at: datetime | None = None


@dataclass(frozen=True)
class MessageStorageEntry:
    bot_id: int
    user_id: int
    user_message: str
    bot_response: str
    created_at: datetime


class InMemoryStorage:
    """Simple repository used by tests and local examples."""

    def __init__(self) -> None:
        self.bots: Dict[int, BotStorageEntry] = {}
        self.messages: List[MessageStorageEntry] = []

    def encrypt_token(self, token: str) -> str:
        """Training-only token pseudo-encryption marker."""
        return f"enc::{token}"

    def save_bot(
        self,
        *,
        bot_id: int,
        bot_username: str,
        owner_id: int,
        token_encrypted: str,
        created_at: datetime | None = None,
    ) -> None:
        created = created_at or utcnow()
        self.bots[bot_id] = BotStorageEntry(
            bot_id=bot_id,
            bot_username=bot_username,
            owner_id=owner_id,
            token_encrypted=token_encrypted,
            created_at=created,
        )

    def save_message(
        self,
        *,
        bot_id: int,
        user_id: int,
        user_message: str,
        bot_response: str,
        created_at: datetime | None = None,
    ) -> None:
        created = created_at or utcnow()
        self.messages.append(
            MessageStorageEntry(
                bot_id=bot_id,
                user_id=user_id,
                user_message=user_message,
                bot_response=bot_response,
                created_at=created,
            )
        )
        bot = self.bots.get(bot_id)
        if bot is None:
            return
        self.bots[bot_id] = BotStorageEntry(
            bot_id=bot.bot_id,
            bot_username=bot.bot_username,
            owner_id=bot.owner_id,
            token_encrypted=bot.token_encrypted,
            created_at=bot.created_at,
            status=bot.status,
            message_count=bot.message_count + 1,
            last_message_at=created,
        )

    def get_bot(self, bot_id: int) -> BotStorageEntry | None:
        return self.bots.get(bot_id)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
