"""Configuration for daily Telegram channel autoposter."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_TOPICS = [
    "Аналитика рынка новостроек Москвы",
    "Объект дня: ликвидная квартира",
    "Совет покупателю: как проверить застройщика",
    "Инвестиционный разбор локации",
    "Ипотека и рассрочка: что выгоднее сегодня",
]


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class AutoposterConfig:
    """Runtime settings loaded from environment variables."""

    telegram_bot_token: str
    telegram_channel_id: str
    moderation_chat_id: str
    moderation_enabled: bool
    moderation_poll_interval_seconds: int
    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str
    openrouter_referer: str
    channel_name: str
    contact_handle: str
    optional_contact_line: str
    topics: list[str]
    state_file: str
    timezone: str
    publish_hour: int
    publish_minute: int
    generation_temperature: float
    generation_max_tokens: int


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Missing required env variable: {name}")
    return value


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"Invalid integer for {name}: {raw}") from exc


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"Invalid float for {name}: {raw}") from exc


def _get_topics() -> list[str]:
    raw = os.getenv("AUTOP_POSTER_TOPICS", "").strip()
    if not raw:
        return DEFAULT_TOPICS
    normalized = raw.replace("|", ";").replace(",", ";")
    topics = [item.strip() for item in normalized.split(";") if item.strip()]
    if not topics:
        raise ConfigError("AUTOP_POSTER_TOPICS is set but contains no valid topics")
    return topics


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()
    if raw in {"1", "true", "yes", "y", "on"}:
        return True
    if raw in {"0", "false", "no", "n", "off"}:
        return False
    raise ConfigError(f"Invalid boolean for {name}: {raw}")


def load_autoposter_config() -> AutoposterConfig:
    """Load and validate autoposter configuration."""
    load_dotenv()
    openrouter_api_key = os.getenv("AUTOP_POSTER_OPENROUTER_API_KEY", "").strip() or _require_env(
        "OPENROUTER_API_KEY"
    )
    return AutoposterConfig(
        telegram_bot_token=_require_env("TELEGRAM_BOT_TOKEN"),
        telegram_channel_id=_require_env("TELEGRAM_CHANNEL_ID"),
        moderation_chat_id=os.getenv("AUTOPOSTER_REVIEWER_CHAT_ID", "").strip()
        or _require_env("TELEGRAM_CHANNEL_ID"),
        moderation_enabled=_get_bool("AUTOPOSTER_ENABLE_MODERATION", True),
        moderation_poll_interval_seconds=_get_int(
            "AUTOPOSTER_MODERATION_POLL_INTERVAL_SECONDS", 0
        ),
        openrouter_api_key=openrouter_api_key,
        openrouter_model=os.getenv("AUTOP_POSTER_MODEL", "openai/gpt-4o-mini").strip(),
        openrouter_base_url=os.getenv(
            "AUTOP_POSTER_BASE_URL", "https://openrouter.io/api/v1/chat/completions"
        ).strip(),
        openrouter_referer=os.getenv("AUTOP_POSTER_REFERER", "https://example.local").strip(),
        channel_name=os.getenv("AUTOPOSTER_CHANNEL_NAME", "НОВОСТРОЙКИ МОСКВЫ").strip(),
        contact_handle=os.getenv("AUTOPOSTER_CONTACT_HANDLE", "@AlexSavushkin").strip(),
        optional_contact_line=os.getenv(
            "AUTOPOSTER_OPTIONAL_CONTACT_LINE", "Связаться со мной в Max"
        ).strip(),
        topics=_get_topics(),
        state_file=os.getenv("AUTOPOSTER_STATE_FILE", ".autoposter_state.json").strip(),
        timezone=os.getenv("AUTOPOSTER_TIMEZONE", "Europe/Moscow").strip(),
        publish_hour=_get_int("AUTOPOSTER_PUBLISH_HOUR", 10),
        publish_minute=_get_int("AUTOPOSTER_PUBLISH_MINUTE", 0),
        generation_temperature=_get_float("AUTOPOSTER_TEMPERATURE", 0.7),
        generation_max_tokens=_get_int("AUTOPOSTER_MAX_TOKENS", 1100),
    )
