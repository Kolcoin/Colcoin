"""Configuration helpers for managed bots training MVP."""

from __future__ import annotations

import os
from dataclasses import dataclass


PLACEHOLDER_TOKENS = {
    "YOUR_MANAGEMENT_BOT_TOKEN_HERE",
    "YOUR_BOT_USERNAME",
    "sk-or-v1-YOUR_KEY_HERE",
}


class SecurityError(ValueError):
    """Raised when a known placeholder or unsafe configuration is detected."""


@dataclass(frozen=True)
class AppConfig:
    """Runtime config sourced from environment variables."""

    management_bot_token: str
    management_bot_username: str
    openrouter_key: str
    openrouter_model: str = "openai/gpt-4-turbo"
    openrouter_referer: str = "https://example.local"


def _read_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SecurityError(f"{name} is not set")
    if value in PLACEHOLDER_TOKENS:
        raise SecurityError(f"{name} still contains a placeholder value")
    return value


def _looks_like_real_bot_token(value: str) -> bool:
    parts = value.split(":", 1)
    if len(parts) != 2:
        return False
    bot_id, secret = parts
    return bot_id.isdigit() and len(secret) >= 20


def load_config() -> AppConfig:
    """Load validated application config from environment."""

    management_bot_token = _read_env("TELEGRAM_MANAGEMENT_BOT_TOKEN")
    openrouter_key = _read_env("OPENROUTER_API_KEY")
    management_bot_username = _read_env("TELEGRAM_MANAGEMENT_BOT_USERNAME")

    # Training guardrail: discourage accidentally using production secrets.
    if _looks_like_real_bot_token(management_bot_token):
        raise SecurityError(
            "Training scaffold expects placeholder bot token, got a real-looking token"
        )
    if openrouter_key.startswith("sk-or-v1-") and len(openrouter_key) > 20:
        raise SecurityError(
            "Training scaffold expects placeholder OpenRouter key, got a real-looking key"
        )

    return AppConfig(
        management_bot_token=management_bot_token,
        management_bot_username=management_bot_username,
        openrouter_key=openrouter_key,
        openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo"),
        openrouter_referer=os.getenv("OPENROUTER_REFERER", "https://example.local"),
    )
