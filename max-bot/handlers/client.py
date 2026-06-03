"""Сценарий клиента (FSM):
  /start  → меню
  «Заказать» → день → время → пакеты → адрес → телефон → подтверждение → оплата
  «Я оплатил» → заказ уходит в группу курьеров

Оплата идёт по внешней ссылке (ЮKassa / СБП). Бот не проверяет факт оплаты —
это MVP. Когда подключим webhook от платёжки, статус будет проставляться автоматом.
"""

from maxapi import (
    CallbackData,
    Command,
    Router,
    State,
    StateFilter,
    StatesGroup,
)

from config import Config
from keyboards import (
    admin_assign_kb,
    bags_kb,
    day_kb,
    pay_kb,
    start_kb,
    time_kb,
)
from pricing import calculate_courier_pay, calculate_price
from storage import create_order, get_order, set_status

router = Router()


class OrderFlow(StatesGroup):
    waiting_address = State()
    waiting_phone = State()


DAY_LABELS = {"today": "Сегодня", "tomorrow": "Завтра"}
TIME_LABELS = {
    "morning": "🌅 Утро 8:00–10:00",
    "evening": "🌆 Вечер 19:00–21:00",
}


# --- /start --------------------------------------------------------------

@router.message_created(Command("start"))
async def cmd_start(event, state):
    await state.clear()
    await event.message.answer(
        "👋 Привет! Выносим мусор прямо от вашей двери.\n\n"
        "🙌 Три шага и всё:\n"
        "1️⃣ Оформи заказ\n"
        "2️⃣ Оплати\n"
        "3️⃣ Выставь пакеты за дверь\n"
        "Остальное — наша работа. 💪\n\n"
        "🕐 Работаем:\n"
        "   🌅 Утро 8:00–10:00\n"
        "   🌆 Вечер 19:00–21:00\n\n"
        "💸 от 150₽",
        keyboard=start_kb(event.bot._support_username or ""),
    )


# --- день -----------------------------------------------------------------

@router.callback_handler(CallbackData("order"))
async def on_order(event, state):
    await state.clear()
    await event.bot.answer_callback(event.callback_id)
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Когда забрать мусор?",
        keyboard=day_kb(),
    )


@router.callback_handler(CallbackData("day:", startswith=True))
async def on_day(event, state):
    key = event.payload_text.split(":", 1)[1]
    await state.update_data(day=DAY_LABELS[key])
    await event.bot.answer_callback(event.callback_id)
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Выбери время:",
        keyboard=time_kb(),
    )


@router.callback_handler(CallbackData("time:", startswith=True))
async def on_time(event, state):
    key = event.payload_text.split(":", 1)[1]
    await state.update_data(time=TIME_LABELS[key])
    await event.bot.answer_callback(event.callback_id)
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Сколько мешков? (макс. 4)",
        keyboard=bags_kb(),
    )


@router.callback_handler(CallbackData("bags:", startswith=True))
async def on_bags(event, state):
    bags = int(event.payload_text.split(":", 1)[1])
    await state.update_data(
        bags=bags,
        price=calculate_price(bags),
        courier_pay=calculate_courier_pay(bags),
    )
    await state.set_state(OrderFlow.waiting_address)
    await event.bot.answer_callback(event.callback_id)
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="📍 Напиши свой АДРЕС (улица, дом, квартира):",
    )


# --- адрес ---------------------------------------------------------------

@router.message_created(StateFilter(OrderFlow.waiting_address))
async def on_address(event, state):
    text = (event.message.body.text or "").strip() if event.message.body else ""
    if len(text) < 5:
        await event.message.answer("Адрес слишком короткий. Напиши подробнее.")
        return
    await state.update_data(address=text)
    await state.set_state(OrderFlow.waiting_phone)
    await event.message.answer("📞 Теперь напиши свой ТЕЛЕФОН:")


# --- телефон + создание заказа ------------------------------------------

@router.message_created(StateFilter(OrderFlow.waiting_phone))
async def on_phone(event, state):
    config: Config = event.bot._config
    phone = (event.message.body.text or "").strip() if event.message.body else ""
    if len(phone) < 5:
        await event.message.answer("Телефон слишком короткий. Напиши ещё раз.")
        return

    data = await state.get_data()
    sender = event.message.sender
    order = create_order(
        client_chat_id=event.chat_id,
        client_user_id=event.user_id or 0,
        client_username=sender.username if sender else None,
        client_name=(sender.first_name or sender.name or "клиент") if sender else "клиент",
        day=data["day"],
        time=data["time"],
        bags=data["bags"],
        address=data["address"],
        phone=phone,
        price=data["price"],
        courier_pay=data["courier_pay"],
    )

    summary = (
        "📋 Проверь заказ:\n\n"
        f"📅 День: {order.day}\n"
        f"🕐 Время: {order.time}\n"
        f"🎒 Мешков: {order.bags}\n"
        f"🏠 Адрес: {order.address}\n"
        f"📞 Телефон: {order.phone}\n"
        f"💰 К оплате: {order.price}₽\n\n"
        "Перейди по ссылке, оплати, потом нажми «✅ Я оплатил(а)»."
    )
    await event.message.answer(summary, keyboard=pay_kb(config.pay_link, order.id))
    await state.clear()


# --- «Я оплатил(а)» -> в группу курьеров + копия админу ------------------

@router.callback_handler(CallbackData("paid:", startswith=True))
async def on_paid(event, state):
    config: Config = event.bot._config
    order_id = int(event.payload_text.split(":", 1)[1])
    order = get_order(order_id)
    if order is None:
        await event.bot.answer_callback(event.callback_id, notification="Заказ не найден")
        return

    # Защита от двойного нажатия.
    if order.status != "awaiting_payment":
        await event.bot.answer_callback(event.callback_id, notification="Заказ уже передан")
        return

    set_status(order_id, "paid")
    await event.bot.answer_callback(event.callback_id, notification="Спасибо!")

    # Клиенту.
    await event.bot.send_message(
        chat_id=event.chat_id,
        text=(
            "✅ Спасибо! Заказ принят.\n\n"
            "Курьер заберёт мусор в выбранное время. "
            "Когда вынесет — пришлёт фото-отчёт сюда."
        ),
    )

    # В группу курьеров.
    username = f"@{order.client_username}" if order.client_username else "нет ника"
    group_text = (
        f"🆕 НОВЫЙ ЗАКАЗ #{order.id}\n\n"
        f"👤 Клиент: {order.client_name} ({username})\n"
        f"📅 День: {order.day}\n"
        f"🕐 Время: {order.time}\n"
        f"🎒 Мешков: {order.bags}\n"
        f"🏠 Адрес: {order.address}\n"
        f"📞 Телефон: {order.phone}\n"
        f"💰 Оплачено: {order.price}₽\n"
        f"🚖 Курьеру: {order.courier_pay}₽"
    )
    await event.bot.send_message(
        chat_id=config.group_id,
        text=group_text,
        keyboard=admin_assign_kb(order.id),
    )

    # Копия админу в личку.
    await event.bot.send_message(
        user_id=config.admin_id,
        text=f"📋 Заказ #{order.id} оплачен.\n\n{group_text}",
    )


# ============================================================================
# TODO: ЗДЕСЬ БУДУТ ПОДПИСКА, АБОНЕМЕНТ, ПРОВЕРКА РЕАЛЬНОЙ ОПЛАТЫ
# ----------------------------------------------------------------------------
# 1) Перед оплатой: проверить consume_abonnement(user_id), если есть — заказ
#    бесплатный, статус сразу "paid", идём в группу.
# 2) Вместо ручной кнопки «Я оплатил» — webhook от ЮKassa/СБП присылает
#    подтверждение → бот сам ставит status="paid" и шлёт в группу.
# 3) Подписка (например, 4 выноса в месяц) — отдельная таблица subscriptions.
# Сейчас MVP без всего этого.
# ============================================================================
