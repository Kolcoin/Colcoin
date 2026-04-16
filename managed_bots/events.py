"""Typed events used by managed bots workflow."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManagedBotOwner:
    """Created managed bot identity."""

    id: int
    username: str


@dataclass(frozen=True)
class ManagedBotInfo:
    """Payload for managed bot creation callback."""

    bot: ManagedBotOwner
    user_id: int


@dataclass(frozen=True)
class ManagedBotEvent:
    """Top-level event envelope."""

    managed_bot: ManagedBotInfo


@dataclass(frozen=True)
class UserMessageEvent:
    """Incoming user message routed through management bot."""

    managed_bot_id: int
    user_id: int
    text: str
