from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_session
from app.schemas import LoginIn, RegisterIn, UserOut
from app.security import (
    COOKIE_NAME,
    create_token,
    current_user,
    hash_password,
    verify_password,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(payload: RegisterIn, response: Response,
                   session: AsyncSession = Depends(get_session)):
    existing = (await session.execute(
        select(User).where(User.email == payload.email)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="email already registered")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        trial_until=datetime.utcnow() + timedelta(days=5),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    token = create_token(user.id)
    response.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", max_age=14 * 86400)
    return user


@router.post("/login", response_model=UserOut)
async def login(payload: LoginIn, response: Response,
                session: AsyncSession = Depends(get_session)):
    user = (await session.execute(
        select(User).where(User.email == payload.email)
    )).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_token(user.id)
    response.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", max_age=14 * 86400)
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(current_user)):
    return user
