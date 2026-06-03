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
    group_id: int
    pay_link: str
    support_username: str


def load_config() -> Config:
    token = os.getenv("MAX_BOT_TOKEN", "").strip()
    admin = os.getenv("ADMIN_ID", "").strip()
    courier = os.getenv("COURIER_ID", "").strip()
    group = os.getenv("GROUP_ID", "").strip()
    pay_link = os.getenv("PAY_LINK", "").strip()
    support = os.getenv("SUPPORT_USERNAME", "").strip().lstrip("@")

    if not token:
        raise RuntimeError("Не задан MAX_BOT_TOKEN в .env")
    for name, raw in (("ADMIN_ID", admin), ("COURIER_ID", courier), ("GROUP_ID", group)):
        if not raw.lstrip("-").isdigit():
            raise RuntimeError(f"{name} должен быть целым числом, сейчас: {raw!r}")
    if not pay_link.startswith(("http://", "https://")):
        raise RuntimeError("PAY_LINK должна быть полной ссылкой (http/https)")

    return Config(
        bot_token=token,
        admin_id=int(admin),
        courier_id=int(courier),
        group_id=int(group),
        pay_link=pay_link,
        support_username=support,
    )
