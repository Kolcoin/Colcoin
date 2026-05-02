"""Имитация поведения живого пользователя в браузере (Playwright).

Внутри: плавные движения мыши, человеческий скролл, опечатки при наборе,
случайные «чтения» с разной длительностью, переходы по внутренним ссылкам.
"""

from __future__ import annotations

import asyncio
import random
import string
from dataclasses import dataclass
from typing import Optional

from playwright.async_api import Page


@dataclass
class BehaviorProfile:
    typing_speed_wpm: int = 220   # знаков в минуту, реальный диапазон 180-320
    typo_chance: float = 0.04
    scroll_step_min: int = 150
    scroll_step_max: int = 480
    read_pause_min: float = 0.4
    read_pause_max: float = 2.6


async def human_sleep(min_s: float, max_s: float) -> None:
    await asyncio.sleep(random.uniform(min_s, max_s))


async def human_type(page: Page, selector: str, text: str,
                     profile: Optional[BehaviorProfile] = None) -> None:
    """Печать с переменной скоростью и иногда — опечатками с исправлением."""
    profile = profile or BehaviorProfile()
    locator = page.locator(selector).first
    await locator.click()
    await human_sleep(0.2, 0.6)

    base_delay = 60.0 / profile.typing_speed_wpm  # сек на символ
    for ch in text:
        if random.random() < profile.typo_chance and ch.isalpha():
            wrong = random.choice(string.ascii_lowercase)
            await page.keyboard.type(wrong, delay=random.uniform(40, 120))
            await human_sleep(0.05, 0.25)
            await page.keyboard.press("Backspace")
            await human_sleep(0.05, 0.2)
        delay_ms = max(15, (base_delay + random.uniform(-0.04, 0.07)) * 1000)
        await page.keyboard.type(ch, delay=delay_ms)


async def human_scroll(page: Page, total_steps: int = 6,
                       profile: Optional[BehaviorProfile] = None) -> None:
    """Скроллит страницу несколькими «человеческими» шагами c паузами для чтения."""
    profile = profile or BehaviorProfile()
    for _ in range(total_steps):
        step = random.randint(profile.scroll_step_min, profile.scroll_step_max)
        if random.random() < 0.18:
            step = -random.randint(60, 200)  # иногда чуть назад
        try:
            await page.mouse.wheel(0, step)
        except Exception:
            await page.evaluate("(s) => window.scrollBy(0, s)", step)
        await human_sleep(profile.read_pause_min, profile.read_pause_max)


async def human_mouse_move(page: Page, points: int = 4) -> None:
    vp = page.viewport_size or {"width": 1280, "height": 800}
    x, y = random.randint(50, vp["width"] - 50), random.randint(50, vp["height"] - 50)
    for _ in range(points):
        nx = max(5, min(vp["width"] - 5, x + random.randint(-220, 220)))
        ny = max(5, min(vp["height"] - 5, y + random.randint(-180, 180)))
        # Playwright сам делает плавный путь при steps>1
        await page.mouse.move(nx, ny, steps=random.randint(8, 25))
        x, y = nx, ny
        await human_sleep(0.05, 0.35)


async def maybe_click_internal_link(page: Page) -> bool:
    """С небольшой вероятностью кликает по случайной внутренней ссылке.
    Возвращает True если переход состоялся."""
    try:
        host = page.url.split("/")[2]
    except Exception:
        return False

    hrefs = await page.evaluate(
        """(host) => Array.from(document.querySelectorAll('a[href]'))
            .map(a => a.href)
            .filter(h => {
                try { const u = new URL(h); return u.host === host && !h.includes('#'); }
                catch(e) { return false; }
            })
            .slice(0, 50)
        """,
        host,
    )
    if not hrefs:
        return False
    target = random.choice(hrefs)
    try:
        await page.goto(target, wait_until="domcontentloaded", timeout=20000)
        return True
    except Exception:
        return False
