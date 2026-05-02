"""Telegram-бот: регистрация, выдача пароля, статусы проектов.

Аналог @umnii_servis_bot. Запуск опциональный (если задан TELEGRAM_BOT_TOKEN).
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta

from sqlalchemy import select

from app.config import settings
from app.db.models import Project, User
from app.db.session import SessionLocal
from app.security import hash_password


log = logging.getLogger(__name__)


async def run_bot() -> None:
    if not settings.telegram_bot_enabled or not settings.telegram_bot_token:
        log.info("telegram bot disabled")
        return

    from aiogram import Bot, Dispatcher, types  # импорт «лениво»
    from aiogram.filters import Command

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(m: types.Message):
        await m.answer(
            "Привет! Этот бот выдаст вам доступ к личному кабинету сервиса "
            "автоматического SEO-продвижения.\n\n"
            "Команды:\n"
            "  /password — получить новый пароль\n"
            "  /status — посмотреть статус проектов"
        )

    @dp.message(Command("password"))
    async def cmd_password(m: types.Message):
        tg_id = str(m.from_user.id)
        email = f"tg_{tg_id}@bot.local"
        new_password = secrets.token_urlsafe(8)
        async with SessionLocal() as session:
            user = (await session.execute(
                select(User).where(User.telegram_id == tg_id)
            )).scalar_one_or_none()
            if user is None:
                user = User(
                    email=email,
                    password_hash=hash_password(new_password),
                    telegram_id=tg_id,
                    trial_until=datetime.utcnow() + timedelta(days=5),
                )
                session.add(user)
            else:
                user.password_hash = hash_password(new_password)
            await session.commit()
        await m.answer(
            f"Ваш доступ:\n\nemail: <code>{email}</code>\n"
            f"пароль: <code>{new_password}</code>\n\n"
            f"Войдите на странице /login.",
            parse_mode="HTML",
        )

    @dp.message(Command("status"))
    async def cmd_status(m: types.Message):
        tg_id = str(m.from_user.id)
        async with SessionLocal() as session:
            user = (await session.execute(
                select(User).where(User.telegram_id == tg_id)
            )).scalar_one_or_none()
            if not user:
                return await m.answer("Сначала получите пароль: /password")
            projects = (await session.execute(
                select(Project).where(Project.user_id == user.id)
            )).scalars().all()
        if not projects:
            return await m.answer("У вас ещё нет проектов. Добавьте их в личном кабинете.")
        lines = ["<b>Ваши проекты:</b>"]
        for p in projects:
            lines.append(
                f"• {p.name} ({p.domain}) — {'🟢 активен' if p.is_active else '⏸ пауза'}, "
                f"тариф {p.plan}, дневная норма визитов: {p.daily_visits_target}"
            )
        await m.answer("\n".join(lines), parse_mode="HTML")

    log.info("starting telegram bot polling")
    await dp.start_polling(bot)
