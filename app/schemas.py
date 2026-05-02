from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ProjectIn(BaseModel):
    name: str
    domain: str
    region: int = 213
    plan: str = "lite"
    daily_visits_target: int = 20
    avg_session_seconds: int = 90


class ProjectOut(BaseModel):
    id: int
    name: str
    domain: str
    region: int
    plan: str
    is_active: bool
    daily_visits_target: int
    avg_session_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True


class KeywordIn(BaseModel):
    query: str
    target_url: Optional[str] = None


class KeywordsBulkIn(BaseModel):
    queries: list[str]


class KeywordOut(BaseModel):
    id: int
    query: str
    target_url: Optional[str]
    last_position: Optional[int]
    last_checked_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class TaskOut(BaseModel):
    id: int
    project_id: int
    keyword_id: int
    status: str
    scheduled_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    found_position: Optional[int]
    session_seconds: Optional[int]
    pages_visited: Optional[int]
    user_agent: Optional[str]
    proxy: Optional[str]

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    email: str
    is_active: bool
    is_admin: bool
    balance: float
    trial_until: Optional[datetime]

    class Config:
        from_attributes = True
