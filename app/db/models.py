from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    telegram_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    trial_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    projects: Mapped[list["Project"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(255))  # example.com
    region: Mapped[int] = mapped_column(Integer, default=213)
    plan: Mapped[str] = mapped_column(String(32), default="lite")  # lite/pro/premium
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_visits_target: Mapped[int] = mapped_column(Integer, default=20)
    avg_session_seconds: Mapped[int] = mapped_column(Integer, default=90)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="projects")
    keywords: Mapped[list["Keyword"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    query: Mapped[str] = mapped_column(String(512))
    target_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    last_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="keywords")
    positions: Mapped[list["PositionHistory"]] = relationship(
        back_populates="keyword", cascade="all, delete-orphan"
    )


class PositionHistory(Base):
    __tablename__ = "position_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"))
    position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    keyword: Mapped["Keyword"] = relationship(back_populates="positions")


class Task(Base):
    """Задача для робота — посетить выдачу по запросу и кликнуть на сайт."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(16), default="pending")
    # pending / running / done / failed
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    found_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    session_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pages_visited: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    proxy: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="tasks")
