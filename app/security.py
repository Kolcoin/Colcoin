from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import User
from app.db.session import get_session


ALGO = "HS256"
TOKEN_LIFETIME = timedelta(days=14)
COOKIE_NAME = "session"


def _safe_pwd_bytes(password: str) -> bytes:
    # bcrypt ограничен 72 байтами — обрезаем
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_safe_pwd_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_safe_pwd_bytes(plain), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + TOKEN_LIFETIME,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGO)


def decode_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGO])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


async def current_user(
    session_token: Optional[str] = Cookie(default=None, alias=COOKIE_NAME),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")
    user_id = decode_token(session_token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    user = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user disabled")
    return user


async def optional_user(
    session_token: Optional[str] = Cookie(default=None, alias=COOKIE_NAME),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    if not session_token:
        return None
    user_id = decode_token(session_token)
    if user_id is None:
        return None
    return (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
