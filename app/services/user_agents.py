"""Пул User-Agent + viewport для роботов.

Используем заранее заготовленный пул реальных современных UA,
чтобы не зависеть от сети/обновлений сторонних библиотек.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


_DESKTOP_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
]

_MOBILE_UAS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
]

_VIEWPORTS_DESKTOP = [
    (1920, 1080),
    (1536, 864),
    (1440, 900),
    (1366, 768),
    (1280, 800),
]

_VIEWPORTS_MOBILE = [
    (390, 844),
    (412, 915),
    (375, 667),
]

_LOCALES = ["ru-RU", "ru-RU", "ru-RU", "en-US"]
_TIMEZONES = [
    "Europe/Moscow",
    "Europe/Moscow",
    "Asia/Yekaterinburg",
    "Europe/Kaliningrad",
]


@dataclass
class Persona:
    user_agent: str
    viewport: tuple[int, int]
    is_mobile: bool
    locale: str
    timezone: str

    @property
    def viewport_dict(self) -> dict:
        return {"width": self.viewport[0], "height": self.viewport[1]}


def random_persona(mobile_chance: float = 0.35) -> Persona:
    is_mobile = random.random() < mobile_chance
    if is_mobile:
        ua = random.choice(_MOBILE_UAS)
        vp = random.choice(_VIEWPORTS_MOBILE)
    else:
        ua = random.choice(_DESKTOP_UAS)
        vp = random.choice(_VIEWPORTS_DESKTOP)
    return Persona(
        user_agent=ua,
        viewport=vp,
        is_mobile=is_mobile,
        locale=random.choice(_LOCALES),
        timezone=random.choice(_TIMEZONES),
    )
