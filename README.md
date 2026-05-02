# AutoPromo — автоматизированный сервис продвижения сайта (аналог «Умного Сервиса»)

Самодостаточный аналог сервисов накрутки **поведенческих факторов (ПФ)**
типа [umnii-servis](https://умныйсервис.рф/). Роботы под видом живых
пользователей заходят на выдачу Яндекса/Google, кликают на ваш сайт и
имитируют посетителя — растут CTR-сниппета, dwell time, last-click
satisfaction и, как следствие, позиции в поиске.

## Что внутри

```
┌──────────────────────────────────────────────────────────────────┐
│                  FastAPI + Jinja UI (личный кабинет)             │
│                  REST /api/auth /api/projects                    │
└────┬─────────────────────────────────────────────────┬───────────┘
     │ SQLite (SQLAlchemy async)                       │
     ▼                                                 ▼
┌──────────────┐  APScheduler          ┌──────────────────────────┐
│  WorkerPool  │◄──── каждые 15 мин ───┤  schedule_daily_tasks    │
│  (asyncio)   │      создаёт пачки    │  refresh_positions_job   │
│              │      задач            │  каждые 6 ч              │
│  ┌────────┐  │                       └──────────────────────────┘
│  │ Robot  │──┤                       Position checker (httpx)
│  │ Playwr │  │
│  └────────┘  │     ┌──────────────────┐
└──────────────┘     │ Telegram-бот     │ (опционально)
                     │ aiogram          │
                     └──────────────────┘
```

### Что делает один «робот»

1. Случайно выбирает persona — UA (desktop/mobile), viewport, locale, timezone.
2. Запускает Chromium через Playwright со stealth-патчами (`navigator.webdriver=undefined` и т.п.).
3. Открывает выдачу: `https://yandex.ru/search/?text=...&lr=...&p=N` (или Google).
4. Имитирует пользователя на странице выдачи: движение мыши, скролл, паузы для «чтения».
5. Листает страницы выдачи, ищет ссылку на ваш домен.
6. Кликает на сниппет вашего сайта (а не идёт по прямому URL!).
7. На сайте имитирует сессию: скролл, переходы по внутренним страницам, длительность 60-180 сек.

### Что хранит БД

- Пользователи / Проекты / Ключи (ограничены тарифом: lite=50, pro=100, premium=300)
- Очередь задач (Tasks): pending → running → done/failed
- История позиций (PositionHistory) — для построения графика динамики

## Быстрый старт (DEMO_MODE — без обращения к Яндексу)

```bash
git clone <this repo> autopromo && cd autopromo
cp .env.example .env

# Вариант 1: docker
docker compose up --build

# Вариант 2: локально
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
uvicorn app.main:app --reload
```

Открыть http://localhost:8000 → зарегистрироваться → создать проект →
загрузить запросы → нажать «▶ Запустить 5 визитов сейчас».

В **DEMO_MODE=1** роботы ходят не на Яндекс, а на встроенный мок-поисковик
(`/mock/serp`), куда автоматически подмешиваются ваши проекты — это
позволяет сразу увидеть весь сценарий end-to-end без капчи и блокировок.

## Боевой режим

В `.env`:
```
DEMO_MODE=0
SEARCH_ENGINE=yandex
YANDEX_REGION=213
PROXY_LIST=http://login:pass@host1:port,http://login:pass@host2:port
WORKER_CONCURRENCY=4
```

Очень важно для боевого использования:
- **Прокси** обязательны (резидентные/мобильные). Без прокси Яндекс быстро покажет капчу.
- **Профили браузеров** — в проде стоит хранить cookies/localStorage между сессиями (в этом MVP — не реализовано).
- **Капча** — Яндекс показывает SmartCaptcha. Решение через антикапчу-сервисы (anti-captcha, RuCaptcha) — точка расширения в `_solve_captcha_if_present`.
- **Yandex XML / Serpstat** — для надёжной проверки позиций замените `position_checker.py`.

## API

- `POST /api/auth/register` `{email, password}` — регистрация (5 дней триал)
- `POST /api/auth/login` — вход
- `GET  /api/projects`
- `POST /api/projects` `{name, domain, region, plan, daily_visits_target, avg_session_seconds}`
- `POST /api/projects/{id}/keywords/bulk` `{queries: [...]}`
- `POST /api/projects/{id}/run-now?count=5` — поставить N задач прямо сейчас
- `GET  /api/projects/{id}/tasks` — последние задачи роботов

## Telegram-бот

Включается в `.env`: `TELEGRAM_BOT_ENABLED=1`, `TELEGRAM_BOT_TOKEN=...`. Команды:
- `/start`
- `/password` — выдать новый пароль (как у `@umnii_servis_bot`)
- `/status` — статус проектов

## Юридический и этический disclaimer

Накрутка поведенческих факторов **противоречит** правилам Яндекса и Google
и может привести к фильтрам/санкциям к домену. Этот код предоставляется
«как есть», в учебных целях для изучения архитектуры подобных сервисов.
Используйте на свой страх и риск; рекомендуется применять для тестов
на собственных стенд-доменах.
