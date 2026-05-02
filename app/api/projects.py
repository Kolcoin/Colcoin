from __future__ import annotations

from datetime import datetime, timedelta
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Keyword, Project, Task, User
from app.db.session import get_session
from app.schemas import (
    KeywordOut,
    KeywordsBulkIn,
    ProjectIn,
    ProjectOut,
    TaskOut,
)
from app.security import current_user


router = APIRouter(prefix="/api", tags=["projects"])


@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(user: User = Depends(current_user),
                        session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(
        select(Project).where(Project.user_id == user.id).order_by(Project.id.desc())
    )).scalars().all()
    return list(rows)


@router.post("/projects", response_model=ProjectOut)
async def create_project(payload: ProjectIn,
                         user: User = Depends(current_user),
                         session: AsyncSession = Depends(get_session)):
    plan_caps = {"lite": (50, 20), "pro": (100, 60), "premium": (300, 200)}
    if payload.plan not in plan_caps:
        raise HTTPException(status_code=400, detail="unknown plan")
    p = Project(
        user_id=user.id,
        name=payload.name,
        domain=payload.domain,
        region=payload.region,
        plan=payload.plan,
        daily_visits_target=payload.daily_visits_target,
        avg_session_seconds=payload.avg_session_seconds,
    )
    session.add(p)
    await session.commit()
    await session.refresh(p)
    return p


async def _get_user_project(session: AsyncSession, user: User, project_id: int) -> Project:
    p = (await session.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )).scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    return p


@router.delete("/projects/{project_id}")
async def delete_project(project_id: int,
                         user: User = Depends(current_user),
                         session: AsyncSession = Depends(get_session)):
    p = await _get_user_project(session, user, project_id)
    await session.delete(p)
    await session.commit()
    return {"ok": True}


@router.post("/projects/{project_id}/toggle")
async def toggle_project(project_id: int,
                         user: User = Depends(current_user),
                         session: AsyncSession = Depends(get_session)):
    p = await _get_user_project(session, user, project_id)
    p.is_active = not p.is_active
    await session.commit()
    return {"ok": True, "is_active": p.is_active}


@router.get("/projects/{project_id}/keywords", response_model=list[KeywordOut])
async def list_keywords(project_id: int,
                        user: User = Depends(current_user),
                        session: AsyncSession = Depends(get_session)):
    await _get_user_project(session, user, project_id)
    rows = (await session.execute(
        select(Keyword).where(Keyword.project_id == project_id).order_by(Keyword.id.desc())
    )).scalars().all()
    return list(rows)


@router.post("/projects/{project_id}/keywords/bulk", response_model=list[KeywordOut])
async def add_keywords_bulk(project_id: int, payload: KeywordsBulkIn,
                            user: User = Depends(current_user),
                            session: AsyncSession = Depends(get_session)):
    project = await _get_user_project(session, user, project_id)
    plan_caps = {"lite": 50, "pro": 100, "premium": 300}
    cap = plan_caps.get(project.plan, 50)
    existing_count = (await session.execute(
        select(Keyword).where(Keyword.project_id == project_id)
    )).scalars().all()
    free = cap - len(existing_count)
    queries = [q.strip() for q in payload.queries if q.strip()][:max(0, free)]
    new_kws = []
    for q in queries:
        kw = Keyword(project_id=project_id, query=q)
        session.add(kw)
        new_kws.append(kw)
    await session.commit()
    for kw in new_kws:
        await session.refresh(kw)
    return new_kws


@router.delete("/projects/{project_id}/keywords/{keyword_id}")
async def delete_keyword(project_id: int, keyword_id: int,
                         user: User = Depends(current_user),
                         session: AsyncSession = Depends(get_session)):
    await _get_user_project(session, user, project_id)
    kw = (await session.execute(
        select(Keyword).where(Keyword.id == keyword_id, Keyword.project_id == project_id)
    )).scalar_one_or_none()
    if not kw:
        raise HTTPException(status_code=404, detail="keyword not found")
    await session.delete(kw)
    await session.commit()
    return {"ok": True}


@router.post("/projects/{project_id}/run-now", response_model=list[TaskOut])
async def run_now(project_id: int, count: int = 3,
                  user: User = Depends(current_user),
                  session: AsyncSession = Depends(get_session)):
    """Поставить N задач прямо сейчас (для теста / ручного буста)."""
    project = await _get_user_project(session, user, project_id)
    kws = (await session.execute(
        select(Keyword).where(
            Keyword.project_id == project_id,
            Keyword.is_active.is_(True),
        )
    )).scalars().all()
    if not kws:
        raise HTTPException(status_code=400, detail="no keywords")
    count = max(1, min(50, count))
    out: list[Task] = []
    for i in range(count):
        kw = random.choice(kws)
        t = Task(
            project_id=project.id,
            keyword_id=kw.id,
            scheduled_at=datetime.utcnow() + timedelta(seconds=i * 2),
        )
        session.add(t)
        out.append(t)
    await session.commit()
    for t in out:
        await session.refresh(t)
    return out


@router.get("/projects/{project_id}/tasks", response_model=list[TaskOut])
async def list_tasks(project_id: int, limit: int = 50,
                     user: User = Depends(current_user),
                     session: AsyncSession = Depends(get_session)):
    await _get_user_project(session, user, project_id)
    rows = (await session.execute(
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(Task.id.desc())
        .limit(min(200, limit))
    )).scalars().all()
    return list(rows)
