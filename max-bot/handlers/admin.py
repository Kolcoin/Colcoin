"""Админ: видит заказы в группе, передаёт их курьеру кнопкой.

Плюс утилита: /id — бот в любом чате (личка / группа) отвечает chat_id и user_id.
Нужно один раз — чтобы заполнить ADMIN_ID, COURIER_ID, GROUP_ID в .env.
"""

from maxapi import CallbackData, Command, Router

from config import Config
from keyboards import courier_done_kb
from storage import get_order, set_status

router = Router()


@router.message_created(Command("id"))
async def cmd_id(event, state):
    await event.message.answer(
        "🆔 Идентификаторы этого чата:\n\n"
        f"chat_id: <code>{event.chat_id}</code>\n"
        f"user_id (твой): <code>{event.user_id}</code>\n\n"
        "Впиши нужное значение в .env и перезапусти бота.",
        format="html",
    )


@router.callback_handler(CallbackData("assign:", startswith=True))
async def on_assign(event, state):
    config: Config = event.bot._config

    if event.user_id != config.admin_id:
        await event.bot.answer_callback(
            event.callback_id,
            notification="Назначать может только админ",
        )
        return

    order_id = int(event.payload_text.split(":", 1)[1])
    order = get_order(order_id)
    if order is None:
        await event.bot.answer_callback(event.callback_id, notification="Заказ не найден")
        return

    if order.status == "assigned":
        await event.bot.answer_callback(event.callback_id, notification="Уже передан")
        return

    set_status(order_id, "assigned")
    await event.bot.answer_callback(event.callback_id, notification="Передано курьеру")

    # Курьеру в личку.
    text = (
        f"🚖 ЗАКАЗ #{order.id} НА ВЫПОЛНЕНИЕ\n\n"
        f"📅 День: {order.day}\n"
        f"🕐 Время: {order.time}\n"
        f"🎒 Мешков: {order.bags}\n"
        f"🏠 Адрес: {order.address}\n"
        f"📞 Телефон: {order.phone}\n"
        f"💵 Твоя оплата: {order.courier_pay}₽\n\n"
        "Как заберёшь — жми «Выполнено» и пришли фото."
    )
    await event.bot.send_message(
        user_id=config.courier_id,
        text=text,
        keyboard=courier_done_kb(order.id),
    )

    # В группе помечаем, что заказ передан.
    await event.bot.send_message(
        chat_id=config.group_id,
        text=f"📦 Заказ #{order.id} передан курьеру.",
    )
