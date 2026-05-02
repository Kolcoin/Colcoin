"""Лёгкий парсер позиций — без использования браузера, через httpx + bs4.

Используется для быстрого еженедельного чек-апа позиций (никаких кликов,
только сбор позиций сайта в выдаче). Для боевых проверок может (и должен)
быть заменён на платный Yandex XML / Serpstat API.
"""

from __future__ import annotations

import re
import urllib.parse
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.services.user_agents import random_persona


def _domain(url_or_domain: str) -> str:
    s = url_or_domain.strip().lower()
    if "://" in s:
        s = s.split("://", 1)[1]
    s = s.split("/")[0]
    if s.startswith("www."):
        s = s[4:]
    return s


async def check_position(
    *,
    query: str,
    target_domain: str,
    region: int = 213,
    engine: str = "yandex",
    max_pages: int = 5,
) -> Optional[int]:
    """Возвращает позицию (1-индекс) или None если сайт не найден в первых N страницах."""

    persona = random_persona(mobile_chance=0.0)
    headers = {
        "User-Agent": persona.user_agent,
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    domain = _domain(target_domain)

    async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
        global_pos = 0
        for page_num in range(max_pages):
            q = urllib.parse.quote_plus(query)
            if engine == "yandex":
                url = f"https://yandex.ru/search/?text={q}&lr={region}&p={page_num}"
            elif engine == "google":
                url = f"https://www.google.com/search?q={q}&hl=ru&start={page_num*10}"
            else:
                url = f"http://localhost:{settings.app_port}/mock/serp?q={q}&page={page_num}"

            try:
                r = await client.get(url)
            except Exception:
                return None
            if r.status_code != 200:
                return None

            soup = BeautifulSoup(r.text, "lxml")
            anchors = []
            if engine == "yandex":
                for item in soup.select("li.serp-item, .serp-item"):
                    a = item.select_one("a.OrganicTitle-Link, a.Link, h2 a, a")
                    if a and a.get("href"):
                        anchors.append(a["href"])
            elif engine == "google":
                for h in soup.select("div#search a h3"):
                    a = h.find_parent("a")
                    if a and a.get("href"):
                        anchors.append(a["href"])
            else:
                for a in soup.select("a.serp-result"):
                    if a.get("href"):
                        anchors.append(a["href"])

            for i, href in enumerate(anchors):
                # абсолютизируем
                if href.startswith("/"):
                    href = "https://yandex.ru" + href
                if domain in _domain(href):
                    return global_pos + i + 1
            global_pos += len(anchors)

    return None
