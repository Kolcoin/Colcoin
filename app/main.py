from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import auth as auth_api
from app.api import mock_serp as mock_api
from app.api import projects as projects_api
from app.bot.telegram_bot import run_bot
from app.config import settings
from app.db.session import init_db
from app.worker.queue import (
    WorkerPool,
    refresh_positions_job,
    schedule_daily_tasks,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s :: %(message)s",
)


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

worker_pool = WorkerPool(concurrency=settings.worker_concurrency)
scheduler = AsyncIOScheduler()
_bot_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await worker_pool.start()
    scheduler.add_job(schedule_daily_tasks, "interval", minutes=15,
                      id="schedule_tasks", replace_existing=True)
    scheduler.add_job(refresh_positions_job, "cron", hour="*/6",
                      id="refresh_positions", replace_existing=True)
    scheduler.start()

    global _bot_task
    if settings.telegram_bot_enabled and settings.telegram_bot_token:
        _bot_task = asyncio.create_task(run_bot())

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        await worker_pool.stop()
        if _bot_task:
            _bot_task.cancel()


app = FastAPI(
    title="AutoPromo — автоматическое SEO-продвижение",
    description="Сервис автоматизированного продвижения сайтов поведенческими факторами",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_api.router)
app.include_router(projects_api.router)
app.include_router(mock_api.router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    if request.cookies.get("session"):
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/healthz")
async def healthz():
    return {"ok": True, "demo_mode": bool(settings.demo_mode)}
