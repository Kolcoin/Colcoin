"""Главный «робот»: открывает поисковик, ищет сайт по запросу,
кликает на сниппет, имитирует поведение пользователя на сайте.

Поддерживает 3 поисковика:
  * yandex     — Яндекс (https://yandex.ru/search/?text=...&lr=...)
  * google     — Google (https://www.google.com/search?q=...)
  * mock       — встроенный локальный мок (для DEMO_MODE и автотестов)

Возвращает структуру с найденной позицией, числом посещённых страниц
и длительностью сессии.
"""

from __future__ import annotations

import asyncio
import random
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

from playwright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from app.config import settings
from app.services.human_behavior import (
    BehaviorProfile,
    human_mouse_move,
    human_scroll,
    human_sleep,
    human_type,
    maybe_click_internal_link,
)
from app.services.user_agents import Persona, random_persona


@dataclass
class RobotResult:
    success: bool
    found_position: Optional[int] = None
    pages_visited: int = 0
    session_seconds: int = 0
    persona: Optional[Persona] = None
    proxy: Optional[str] = None
    log: list[str] = field(default_factory=list)
    error: Optional[str] = None

    def add(self, msg: str) -> None:
        self.log.append(msg)


def _domain(url_or_domain: str) -> str:
    s = url_or_domain.strip().lower()
    if "://" in s:
        s = s.split("://", 1)[1]
    s = s.split("/")[0]
    if s.startswith("www."):
        s = s[4:]
    return s


async def _new_context(p: Playwright, persona: Persona, proxy: Optional[str]) -> BrowserContext:
    launch_kwargs = {
        "headless": bool(settings.playwright_headless),
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    }
    if proxy:
        launch_kwargs["proxy"] = {"server": proxy}

    browser = await p.chromium.launch(**launch_kwargs)
    context = await browser.new_context(
        user_agent=persona.user_agent,
        viewport=persona.viewport_dict,
        locale=persona.locale,
        timezone_id=persona.timezone,
        is_mobile=persona.is_mobile,
        device_scale_factor=2 if persona.is_mobile else 1,
        java_script_enabled=True,
    )

    # Минимальный stealth: маскируем navigator.webdriver и language
    await context.add_init_script(
        """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en'] });
        window.chrome = window.chrome || { runtime: {} };
        """
    )
    return context


def _build_search_url(engine: str, query: str, region: int, page_num: int = 0) -> str:
    q = urllib.parse.quote_plus(query)
    if engine == "yandex":
        # p — это номер страницы (0-индексированный) у Яндекса
        return f"https://yandex.ru/search/?text={q}&lr={region}&p={page_num}"
    if engine == "google":
        start = page_num * 10
        return f"https://www.google.com/search?q={q}&hl=ru&start={start}"
    # mock-режим
    return f"http://localhost:{settings.app_port}/mock/serp?q={q}&page={page_num}"


async def _collect_serp_links(page: Page, engine: str) -> list[tuple[str, str, str]]:
    """Возвращает список кортежей (effective_domain, href, селектор-якоря) для
    органических результатов. effective_domain используется для матчинга
    домена клиента (в mock-режиме отличается от href, потому что href ведёт
    на встроенный демо-сайт)."""
    if engine == "yandex":
        return await page.evaluate(
            """() => Array.from(document.querySelectorAll('li.serp-item, .serp-item'))
                .map((item, i) => {
                    const a = item.querySelector('a.OrganicTitle-Link, a.Link, h2 a, a');
                    if (!a) return null;
                    a.setAttribute('data-bot-idx', i);
                    let host = '';
                    try { host = new URL(a.href).host; } catch(e) {}
                    return [host, a.href, `[data-bot-idx="${i}"]`];
                })
                .filter(Boolean)
            """
        )
    if engine == "google":
        return await page.evaluate(
            """() => Array.from(document.querySelectorAll('div#search a h3'))
                .map((h, i) => {
                    const a = h.closest('a');
                    if (!a) return null;
                    a.setAttribute('data-bot-idx', i);
                    let host = '';
                    try { host = new URL(a.href).host; } catch(e) {}
                    return [host, a.href, `[data-bot-idx="${i}"]`];
                })
                .filter(Boolean)
            """
        )
    return await page.evaluate(
        """() => Array.from(document.querySelectorAll('a.serp-result'))
            .map((a, i) => {
                a.setAttribute('data-bot-idx', i);
                const real = a.getAttribute('data-real-domain') || '';
                let host = real;
                if (!host) { try { host = new URL(a.href).host; } catch(e) {} }
                return [host, a.href, `[data-bot-idx="${i}"]`];
            })
        """
    )


async def _solve_captcha_if_present(page: Page, result: RobotResult) -> bool:
    """Грубая проверка на капчу. Возвращает True если её нет или удалось обойти."""
    try:
        url = page.url
        content = await page.content()
        if "showcaptcha" in url or "captcha" in url.lower() or "Подтвердите, что запросы" in content:
            result.add(f"captcha detected at {url}")
            # В демо/MVP — мы не пытаемся решать капчу
            return False
    except Exception:
        pass
    return True


async def _imitate_on_target_site(page: Page, project_session_seconds: int,
                                  result: RobotResult) -> None:
    """После клика на сайт клиента — имитируем «живого» посетителя."""
    profile = BehaviorProfile()
    target_seconds = max(20, project_session_seconds + random.randint(-15, 30))
    started = time.monotonic()
    visited = 1

    while time.monotonic() - started < target_seconds:
        await human_mouse_move(page, points=random.randint(2, 5))
        await human_scroll(page, total_steps=random.randint(3, 7), profile=profile)

        elapsed = time.monotonic() - started
        if elapsed >= target_seconds:
            break

        # ~50% шанс уйти по внутренней ссылке (но не более 4 страниц)
        if visited < 4 and random.random() < 0.55:
            jumped = await maybe_click_internal_link(page)
            if jumped:
                visited += 1
                result.add(f"jumped to internal page #{visited}: {page.url}")
                await human_sleep(1.0, 2.5)
        else:
            await human_sleep(0.6, 1.8)

    result.pages_visited = visited


async def run_robot_task(
    *,
    query: str,
    target_domain: str,
    region: int,
    engine: str,
    avg_session_seconds: int,
    proxy: Optional[str] = None,
    max_serp_pages: Optional[int] = None,
) -> RobotResult:
    """Выполняет одну задачу: поиск -> клик на нужный домен -> сессия на сайте."""

    persona = random_persona()
    result = RobotResult(success=False, persona=persona, proxy=proxy)
    domain = _domain(target_domain)
    max_pages = max_serp_pages or settings.max_serp_pages
    started_at = time.monotonic()

    try:
        async with async_playwright() as p:
            context = await _new_context(p, persona, proxy)
            page = await context.new_page()

            found_position: Optional[int] = None
            current_global_pos = 0

            for page_num in range(max_pages):
                url = _build_search_url(engine, query, region, page_num)
                result.add(f"open SERP page {page_num + 1}: {url}")
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    result.add(f"goto failed: {e}")
                    continue

                if not await _solve_captcha_if_present(page, result):
                    result.error = "captcha"
                    await context.close()
                    result.session_seconds = int(time.monotonic() - started_at)
                    return result

                await human_sleep(0.8, 2.0)
                await human_mouse_move(page, points=random.randint(2, 4))
                await human_scroll(page, total_steps=random.randint(2, 5))

                # Дожидаемся появления хотя бы одного результата (если SERP уже загружен)
                try:
                    selector = {
                        "yandex": "li.serp-item a, .serp-item a",
                        "google": "div#search a h3",
                    }.get(engine, "a.serp-result")
                    await page.wait_for_selector(selector, timeout=8000)
                except Exception as e:
                    result.add(f"  serp selector wait failed: {e}")
                links = await _collect_serp_links(page, engine)
                result.add(f"  collected {len(links)} organic links on this SERP page")
                if not links:
                    body_len = await page.evaluate("() => document.body ? document.body.innerHTML.length : 0")
                    result.add(f"  debug body_len={body_len}, url={page.url}")

                hit_idx_on_page: Optional[int] = None
                hit_selector: Optional[str] = None
                for idx, (eff_domain, href, selector) in enumerate(links):
                    candidates = [_domain(eff_domain), _domain(href)]
                    if any(domain in c for c in candidates if c):
                        hit_idx_on_page = idx
                        hit_selector = selector
                        found_position = current_global_pos + idx + 1
                        break
                current_global_pos += len(links)

                if hit_selector is not None:
                    result.add(f"  TARGET FOUND at global position {found_position}, clicking...")
                    try:
                        loc = page.locator(hit_selector).first
                        await loc.scroll_into_view_if_needed(timeout=5000)
                        await human_sleep(0.4, 1.2)
                        async with page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                            await loc.click()
                        result.add(f"  landed on: {page.url}")
                        result.found_position = found_position
                        await _imitate_on_target_site(page, avg_session_seconds, result)
                        result.success = True
                        break
                    except Exception as e:
                        result.add(f"  click navigation failed: {e}")
                        result.error = f"click_failed: {e}"
                        break
                else:
                    # пагинация: пауза, чтобы выглядеть как человек
                    await human_sleep(1.2, 3.0)

            if not result.success and result.error is None:
                result.error = "not_found_in_top_pages"

            await context.close()

    except Exception as e:
        result.error = f"engine_error: {e}"
        result.add(f"engine_error: {e}")

    result.session_seconds = int(time.monotonic() - started_at)
    return result
