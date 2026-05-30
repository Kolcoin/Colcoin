"""Конфигурация бота: читаем .env и валидируем."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_id: int
    courier_id: int


def load_config() -> Config:
    """Читает переменные окружения. Падает с понятной ошибкой, если чего-то нет."""
    token = os.getenv("BOT_TOKEN", "").strip()
    admin_raw = os.getenv("ADMIN_ID", "").strip()
    courier_raw = os.getenv("COURIER_ID", "").strip()

    if not token:
        raise RuntimeError("Не задан BOT_TOKEN в .env")
    if not admin_raw.isdigit():
        raise RuntimeError("ADMIN_ID должен быть числом (Telegram ID админа)")
    if not courier_raw.isdigit():
        raise RuntimeError("COURIER_ID должен быть числом (Telegram ID курьера)")

    return Config(
        bot_token=token,
        admin_id=int(admin_raw),
        courier_id=int(courier_raw),
    )
