"""Простая asyncio-очередь воркеров для запуска роботов и проверки позиций.

Подходит для MVP / single-host. На масштаб — заменить на Celery/Redis Queue.
"""

from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Keyword, PositionHistory, Project, Task
from app.db.session import SessionLocal
from app.services.position_checker import check_position
from app.services.robot import run_robot_task

log = logging.getLogger(__name__)


class WorkerPool:
    def __init__(self, concurrency: int) -> None:
        self.concurrency = concurrency
        self._tasks: list[asyncio.Task] = []
        self._stop = asyncio.Event()

    async def start(self) -> None:
        for i in range(self.concurrency):
            self._tasks.append(asyncio.create_task(self._worker(i)))
        log.info("worker pool started: %s workers", self.concurrency)

    async def stop(self) -> None:
        self._stop.set()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def _worker(self, wid: int) -> None:
        log.info("[worker %s] online", wid)
        while not self._stop.is_set():
            try:
                async with SessionLocal() as session:
                    task = await self._claim_task(session)
                if task is None:
                    await asyncio.sleep(3)
                    continue
                await self._run_task(task)
                # человекоподобная пауза между задачами
                await asyncio.sleep(random.randint(settings.task_min_delay,
                                                   settings.task_max_delay))
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.exception("[worker %s] crashed: %s", wid, e)
                await asyncio.sleep(5)

    async def _claim_task(self, session: AsyncSession) -> Optional[Task]:
        now = datetime.utcnow()
        q = (
            select(Task)
            .where(Task.status == "pending", Task.scheduled_at <= now)
            .order_by(Task.scheduled_at.asc())
            .limit(1)
        )
        task = (await session.execute(q)).scalar_one_or_none()
        if not task:
            return None
        task.status = "running"
        task.started_at = now
        await session.commit()
        await session.refresh(task)
        return task

    async def _run_task(self, task: Task) -> None:
        engine = settings.search_engine if not settings.demo_mode else "mock"
        proxy = random.choice(settings.proxies) if settings.proxies else None

        async with SessionLocal() as session:
            kw = (await session.execute(
                select(Keyword).where(Keyword.id == task.keyword_id)
            )).scalar_one_or_none()
            project = (await session.execute(
                select(Project).where(Project.id == task.project_id)
            )).scalar_one_or_none()
            if kw is None or project is None:
                task_obj = (await session.execute(
                    select(Task).where(Task.id == task.id)
                )).scalar_one()
                task_obj.status = "failed"
                task_obj.finished_at = datetime.utcnow()
                task_obj.log = "keyword or project missing"
                await session.commit()
                return
            query = kw.query
            domain = project.domain
            region = project.region
            session_seconds = project.avg_session_seconds

        log.info("[task %s] starting: q=%r domain=%s engine=%s",
                 task.id, query, domain, engine)
        result = await run_robot_task(
            query=query,
            target_domain=domain,
            region=region,
            engine=engine,
            avg_session_seconds=session_seconds,
            proxy=proxy,
        )
        log.info("[task %s] done: success=%s pos=%s pages=%s sec=%s err=%s",
                 task.id, result.success, result.found_position,
                 result.pages_visited, result.session_seconds, result.error)

        async with SessionLocal() as session:
            t = (await session.execute(select(Task).where(Task.id == task.id))).scalar_one()
            t.status = "done" if result.success else "failed"
            t.finished_at = datetime.utcnow()
            t.found_position = result.found_position
            t.session_seconds = result.session_seconds
            t.pages_visited = result.pages_visited
            t.user_agent = result.persona.user_agent if result.persona else None
            t.proxy = result.proxy
            t.log = "\n".join(result.log + ([f"ERROR: {result.error}"] if result.error else []))

            if result.found_position is not None:
                kw = (await session.execute(
                    select(Keyword).where(Keyword.id == t.keyword_id)
                )).scalar_one()
                kw.last_position = result.found_position
                kw.last_checked_at = datetime.utcnow()
                session.add(PositionHistory(
                    keyword_id=kw.id,
                    position=result.found_position,
                    checked_at=datetime.utcnow(),
                ))
            await session.commit()


# ====== Планировщик: создаёт пачки задач каждые N минут ======

async def schedule_daily_tasks() -> None:
    """Раз в час пересоздаёт «пачку» задач на ближайший час пропорционально
    daily_visits_target проекта."""
    async with SessionLocal() as session:
        projects = (await session.execute(
            select(Project).where(Project.is_active.is_(True))
        )).scalars().all()
        for p in projects:
            kws = (await session.execute(
                select(Keyword).where(
                    Keyword.project_id == p.id,
                    Keyword.is_active.is_(True),
                )
            )).scalars().all()
            if not kws:
                continue
            # сколько визитов на ближайший час: 1/24 от дневной нормы (минимум 1)
            visits_this_hour = max(1, p.daily_visits_target // 24)
            for _ in range(visits_this_hour):
                kw = random.choice(kws)
                # размазать запуск равномерно по часу
                offset = random.randint(0, 3599)
                session.add(Task(
                    project_id=p.id,
                    keyword_id=kw.id,
                    scheduled_at=datetime.utcnow() + timedelta(seconds=offset),
                ))
        await session.commit()
    log.info("scheduled hourly task batch")


async def refresh_positions_job() -> None:
    """Обновляет last_position по всем активным ключам без посещений (легкий чек)."""
    engine = settings.search_engine if not settings.demo_mode else "mock"
    async with SessionLocal() as session:
        kws = (await session.execute(
            select(Keyword).where(Keyword.is_active.is_(True))
        )).scalars().all()
        for kw in kws:
            project = (await session.execute(
                select(Project).where(Project.id == kw.project_id)
            )).scalar_one_or_none()
            if not project or not project.is_active:
                continue
            try:
                pos = await check_position(
                    query=kw.query,
                    target_domain=project.domain,
                    region=project.region,
                    engine=engine,
                    max_pages=5,
                )
            except Exception as e:
                log.warning("position check failed for kw=%s: %s", kw.id, e)
                continue
            kw.last_position = pos
            kw.last_checked_at = datetime.utcnow()
            session.add(PositionHistory(
                keyword_id=kw.id, position=pos,
                checked_at=datetime.utcnow(),
            ))
        await session.commit()
    log.info("refreshed positions for %s keywords", len(kws))
