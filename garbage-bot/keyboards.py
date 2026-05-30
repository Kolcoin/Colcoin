"""Клавиатуры (inline и reply) для бота."""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def main_menu_kb() -> ReplyKeyboardMarkup:
    """Главная клавиатура клиента: одна большая кнопка."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🗑 Вынести мусор")]],
        resize_keyboard=True,
    )


def bags_count_kb() -> InlineKeyboardMarkup:
    """Выбор количества пакетов: 1 / 2 / 3."""
    buttons = [
        InlineKeyboardButton(text=str(n), callback_data=f"bags:{n}")
        for n in (1, 2, 3)
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def courier_accept_kb(order_id: int) -> InlineKeyboardMarkup:
    """Кнопка курьера: принять заказ."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text=f"✅ Принять заказ #{order_id}",
                callback_data=f"accept:{order_id}",
            )
        ]]
    )
