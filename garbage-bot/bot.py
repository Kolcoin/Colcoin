"""Точка входа: создаём бота, регистрируем роутеры, запускаем поллинг."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config
from handlers import client, courier


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = load_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # MemoryStorage — состояния FSM хранятся в памяти. Достаточно для MVP.
    # TODO: при подключении БД заменить на RedisStorage или иное персистентное.
    dp = Dispatcher(storage=MemoryStorage())

    # Прокидываем config во все хендлеры через DI aiogram.
    dp["config"] = config

    dp.include_router(client.router)
    dp.include_router(courier.router)

    logging.info("Бот запущен. Админ=%s, курьер=%s", config.admin_id, config.courier_id)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
