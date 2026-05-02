"""Встроенный «мок-Яндекс»: для DEMO_MODE и тестов.

Позволяет полностью прогнать сценарий «робот зашёл -> увидел сайт ->
кликнул -> погулял по сайту» без обращения к реальным поисковикам.
"""

from __future__ import annotations

import hashlib
import math
from urllib.parse import quote_plus, unquote_plus

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.config import settings
from app.db.models import Project, Keyword
from app.db.session import get_session


router = APIRouter(prefix="/mock", tags=["mock"])


PER_PAGE = 10
TOTAL_RESULTS = 50


def _seeded_results(query: str, *, total: int = TOTAL_RESULTS) -> list[dict]:
    """Детерминированный пул «случайных» сайтов в выдаче."""
    h = hashlib.sha256(query.lower().encode("utf-8")).digest()
    pool = [
        ("vc.ru", "Полный гайд по теме"),
        ("habr.com", "Лучшие практики"),
        ("dzen.ru", "Подборка"),
        ("ozon.ru", "Купить"),
        ("wildberries.ru", "Каталог"),
        ("market.yandex.ru", "Цены и отзывы"),
        ("youtube.com", "Видеоразбор"),
        ("pikabu.ru", "Обсуждение"),
        ("livejournal.com", "Личный опыт"),
        ("ria.ru", "Новости"),
        ("kommersant.ru", "Аналитика"),
        ("rbc.ru", "Экспертное мнение"),
        ("lenta.ru", "Обзор"),
        ("avito.ru", "Объявления"),
        ("youla.ru", "Найти"),
        ("ya.ru", "Сервис"),
        ("zoon.ru", "Рейтинг"),
        ("otzovik.com", "Отзывы"),
        ("kp.ru", "Статья"),
        ("aif.ru", "Колонка"),
    ]
    results = []
    for i in range(total):
        idx = (h[i % len(h)] + i * 7) % len(pool)
        domain, title_prefix = pool[idx]
        results.append({
            "url": f"https://{domain}/{quote_plus(query.lower())}-{i+1}",
            "title": f"{title_prefix}: {query} — позиция {i + 1}",
            "snippet": (
                f"Подробный материал по запросу «{query}». Узнайте больше — "
                f"страница {math.ceil((i+1)/PER_PAGE)} результата #{i+1}."
            ),
        })
    return results


async def _inject_user_sites(query: str, results: list[dict],
                             session: AsyncSession) -> list[dict]:
    """Подмешиваем сайты пользователей в выдачу — чтобы роботы их находили.

    Если пользовательский ключ совпал с поисковым запросом, его сайт
    оказывается на детерминированной позиции внутри топ-30.
    """
    matches = (await session.execute(
        select(Keyword, Project).join(Project, Project.id == Keyword.project_id)
        .where(Keyword.query == query, Keyword.is_active.is_(True),
               Project.is_active.is_(True))
    )).all()
    for kw, project in matches:
        # позиция = детерминированная функция от домена + текущего last_position
        h = int(hashlib.sha1(project.domain.encode()).hexdigest(), 16)
        target_pos = (h % 28) + 1  # 1..28
        # каждое посещение немного «улучшает» позицию (имитация ПФ-эффекта)
        if kw.last_position and kw.last_position > 1:
            target_pos = max(1, min(target_pos, kw.last_position - 1))
        # вставляем (или заменяем) на позицию target_pos
        target_idx = target_pos - 1
        # если уже встречается в выдаче на нужной позиции — пропускаем
        if any(project.domain in r["url"] for r in results[:target_idx + 1]):
            continue
        # В DEMO_MODE ссылку ведём на наш мок-сайт — но в "видимый" URL запишем
        # настоящий домен клиента, чтобы детектор позиций его всё равно нашёл.
        mock_site_url = (
            f"http://localhost:{settings.app_port}/mock/site"
            f"?domain={project.domain}&q={quote_plus(query)}"
        )
        results.insert(target_idx, {
            "url": mock_site_url,
            "display_url": f"https://{project.domain}/?utm=mock&q={quote_plus(query)}",
            "title": f"{project.name} — официальный сайт",
            "snippet": f"Сайт «{project.name}». {query} — выгодные предложения, отзывы, цены.",
            "user_domain": project.domain,
        })
    return results


@router.get("/serp", response_class=HTMLResponse)
async def mock_serp(q: str = Query(..., min_length=1),
                    page: int = Query(0, ge=0),
                    session: AsyncSession = Depends(get_session)):
    results = _seeded_results(q)
    results = await _inject_user_sites(q, results, session)
    start = page * PER_PAGE
    page_results = results[start:start + PER_PAGE]

    items_html = ""
    for r in page_results:
        # В выдачу пишем data-real-domain — детектор робота использует его
        # как «эффективный домен» вместо хоста ссылки (в моке href ведёт на /mock/site).
        real_domain = r.get("user_domain") or r["url"].split("/")[2]
        display = r.get("display_url", r["url"])
        items_html += (
            f'<li class="serp-item">'
            f'  <a class="serp-result" href="{r["url"]}" data-real-domain="{real_domain}">{r["title"]}</a>'
            f'  <div class="display-url">{display}</div>'
            f'  <p class="snippet">{r["snippet"]}</p>'
            f'</li>'
        )

    pagination_html = ""
    pages_total = math.ceil(len(results) / PER_PAGE)
    for i in range(pages_total):
        cls = "active" if i == page else ""
        pagination_html += f'<a class="page {cls}" href="/mock/serp?q={quote_plus(q)}&page={i}">{i+1}</a>'

    html = f"""
    <!doctype html>
    <html lang="ru">
    <head>
      <meta charset="utf-8" />
      <title>Мок-выдача — {q}</title>
      <style>
        body {{ font-family: -apple-system, Roboto, Arial; max-width: 800px; margin: 24px auto; color: #222; }}
        h1 {{ font-size: 18px; }}
        ul {{ list-style: none; padding: 0; }}
        li.serp-item {{ margin: 16px 0; padding: 12px; border-bottom: 1px solid #eee; }}
        a.serp-result {{ color: #1a0dab; font-size: 18px; text-decoration: none; }}
        a.serp-result:hover {{ text-decoration: underline; }}
        p.snippet {{ color: #444; margin: 6px 0 0; font-size: 14px; }}
        .pagination {{ margin-top: 20px; }}
        .pagination a {{ padding: 6px 10px; margin-right: 4px; border: 1px solid #ddd; text-decoration: none; color: #333; border-radius: 4px; }}
        .pagination a.active {{ background: #1a0dab; color: white; border-color: #1a0dab; }}
        form {{ margin-bottom: 18px; }}
        input[type=text] {{ padding: 8px; width: 60%; border: 1px solid #aaa; border-radius: 4px; }}
        button {{ padding: 8px 14px; border-radius: 4px; border: 1px solid #1a0dab; background: #1a0dab; color: white; cursor: pointer; }}
      </style>
    </head>
    <body>
      <h1>Мок-выдача поисковика по запросу: «{q}»</h1>
      <form action="/mock/serp" method="get">
        <input type="text" name="q" value="{q}" />
        <button type="submit">Найти</button>
      </form>
      <ul>
        {items_html}
      </ul>
      <div class="pagination">{pagination_html}</div>
      <p style="color:#888;font-size:12px">Это локальный мок. В продакшене — Яндекс/Google.</p>
    </body>
    </html>
    """
    return HTMLResponse(html)


@router.get("/site", response_class=HTMLResponse)
async def mock_site():
    """Демо-сайт «клиента» с несколькими внутренними страницами."""
    return HTMLResponse("""
    <!doctype html>
    <html lang="ru"><head><meta charset="utf-8"><title>Демо-сайт клиента</title>
    <style>body{font-family:Arial;max-width:760px;margin:30px auto;color:#222}
      h1{color:#1a0dab} a{color:#1a0dab} nav a{margin-right:12px}
      .hero{padding:40px;background:#f4f6fb;border-radius:10px}
    </style></head><body>
      <nav><a href="/mock/site">Главная</a><a href="/mock/site?p=catalog">Каталог</a>
           <a href="/mock/site?p=about">О нас</a><a href="/mock/site?p=contacts">Контакты</a></nav>
      <div class="hero"><h1>Добро пожаловать!</h1>
      <p>Это пример клиентского сайта, на котором робот имитирует поведение посетителя.</p></div>
      <section><h2>Услуги</h2>
        <ul><li><a href="/mock/site?p=service1">Услуга 1</a></li>
            <li><a href="/mock/site?p=service2">Услуга 2</a></li>
            <li><a href="/mock/site?p=service3">Услуга 3</a></li></ul></section>
    </body></html>
    """)
