"""Core service logic for Telegram Managed Bots training examples."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

from .events import ManagedBotEvent, UserMessageEvent
from .storage import InMemoryStorage

GetManagedBotToken = Callable[[int, int], Awaitable[str]]
SendMessage = Callable[[str, int, str], Awaitable[None]]
ProcessWithAI = Callable[[str, dict[str, int]], Awaitable[str]]
SendReply = Callable[[int, int, str], Awaitable[None]]

WELCOME_TEXT = (
    "🤖 Привет! Я создана специально для тебя!\n\n"
    "Я помогу тебе с вопросами. Просто напиши свой запрос."
)


@dataclass
class ManagedBotService:
    """Coordinates bot-created and message-received workflows."""

    storage: InMemoryStorage

    async def on_managed_bot_created(
        self,
        event: ManagedBotEvent,
        *,
        get_managed_bot_token: GetManagedBotToken,
        send_message: SendMessage,
    ) -> None:
        """Persist created bot metadata and send first welcome message."""
        bot_id = event.managed_bot.bot.id
        owner_id = event.managed_bot.user_id
        username = event.managed_bot.bot.username

        token = await get_managed_bot_token(owner_id, bot_id)
        token_encrypted = self.storage.encrypt_token(token)
        self.storage.save_bot(
            bot_id=bot_id,
            bot_username=username,
            owner_id=owner_id,
            token_encrypted=token_encrypted,
        )
        await send_message(token, owner_id, WELCOME_TEXT)

    async def on_managed_bot_message(
        self,
        event: UserMessageEvent,
        *,
        process_with_ai: ProcessWithAI,
        send_reply: SendReply,
    ) -> str:
        """Process user text with AI, reply back, and log conversation."""
        context = {
            "user_id": event.user_id,
            "managed_bot_id": event.managed_bot_id,
        }
        answer = await process_with_ai(event.text, context)
        await send_reply(event.managed_bot_id, event.user_id, answer)
        self.storage.save_message(
            bot_id=event.managed_bot_id,
            user_id=event.user_id,
            user_message=event.text,
            bot_response=answer,
        )
        return answer
