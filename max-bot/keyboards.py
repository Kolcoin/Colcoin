"""Клавиатуры. В MAX используется InlineKeyboardBuilder из maxapi."""

from maxapi import InlineKeyboardBuilder

from pricing import MAX_BAGS


def start_kb(support_username: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.callback("🚀 Заказать вынос мусора", payload="order")
    kb.row()
    if support_username:
        kb.link("💬 Поддержка", url=f"https://max.ru/{support_username}")
        kb.row()
    return kb


def day_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.callback("📅 Сегодня", payload="day:today")
    kb.callback("📅 Завтра", payload="day:tomorrow")
    kb.row()
    return kb


def time_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.callback("🌅 Утро (8:00–10:00)", payload="time:morning")
    kb.row()
    kb.callback("🌆 Вечер (19:00–21:00)", payload="time:evening")
    kb.row()
    return kb


def bags_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for n in range(1, MAX_BAGS + 1):
        kb.callback(f"{n} 🎒", payload=f"bags:{n}")
    kb.row()
    return kb


def pay_kb(pay_link: str, order_id: int) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.link("💳 Перейти к оплате", url=pay_link)
    kb.row()
    kb.callback("✅ Я оплатил(а)", payload=f"paid:{order_id}")
    kb.row()
    return kb


def admin_assign_kb(order_id: int) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.callback(f"📦 Передать курьеру #{order_id}", payload=f"assign:{order_id}")
    kb.row()
    return kb


def courier_done_kb(order_id: int) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.callback(f"✅ Выполнено #{order_id}", payload=f"done:{order_id}")
    kb.row()
    return kb
