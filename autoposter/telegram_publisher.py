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

class TelegramBotApi:
    """Low-level Telegram Bot API helper for moderation flows."""

    def __init__(self, bot_token: str) -> None:
        self._base = f"https://api.telegram.org/bot{bot_token}"

    async def send_message(
        self,
        *,
        chat_id: str,
        text: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True,
        reply_markup: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return await self._post("sendMessage", payload)

    async def edit_message_reply_markup(
        self,
        *,
        chat_id: str,
        message_id: int,
        reply_markup: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"chat_id": chat_id, "message_id": message_id}
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return await self._post("editMessageReplyMarkup", payload)

    async def answer_callback_query(
        self,
        *,
        callback_query_id: str,
        text: str,
        show_alert: bool = False,
    ) -> dict[str, Any]:
        payload = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
        }
        return await self._post("answerCallbackQuery", payload)

    async def get_updates(self, *, offset: int, timeout: int = 20) -> list[dict[str, Any]]:
        payload = {"offset": offset, "timeout": timeout}
        data = await self._post("getUpdates", payload)
        return data.get("result", [])

    async def _post(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = f"{self._base}/{method}"
        async with httpx.AsyncClient(timeout=35.0) as client:
            response = await client.post(endpoint, json=payload)
            response.raise_for_status()
        data: dict[str, Any] = response.json()
        if not data.get("ok"):
            raise TelegramPublishError(str(data))
        return data
