"""Точка входа: создаём бота, регистрируем роутеры, FSM, поллинг."""

import asyncio
import logging

from maxapi import Bot, Dispatcher, MemoryStorage

from config import load_config
from handlers import admin, client, courier


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = load_config()

    bot = Bot(token=config.bot_token)
    # Прокидываем конфиг и поля для UI прямо на bot — хендлеры берут оттуда.
    # Делаем как простой атрибут (не используем глобал, чтобы тестировать было проще).
    bot._config = config
    bot._support_username = config.support_username

    dp = Dispatcher(storage=MemoryStorage())
    dp.setup_fsm()
    dp.include_router(client.router)
    dp.include_router(admin.router)
    dp.include_router(courier.router)

    logging.info(
        "Бот запущен. ADMIN_ID=%s COURIER_ID=%s GROUP_ID=%s",
        config.admin_id, config.courier_id, config.group_id,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
