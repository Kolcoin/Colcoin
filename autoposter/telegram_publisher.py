"""Telegram publishing helpers for channel autoposting."""

from __future__ import annotations

from typing import Any

import httpx

from .config import AutoposterConfig


class TelegramPublishError(RuntimeError):
    """Raised when Telegram API returns an error."""


class TelegramPublisher:
    """Small wrapper around Telegram Bot API `sendMessage` endpoint."""

    def __init__(self, config: AutoposterConfig) -> None:
        self._token = config.telegram_bot_token
        self._channel_id = config.telegram_channel_id

    async def publish_text(
        self,
        text: str,
        *,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
    ) -> dict[str, Any]:
        """Publish one text post to configured Telegram channel."""
        endpoint = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload = {
            "chat_id": self._channel_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise TelegramPublishError(str(data))
        return data
