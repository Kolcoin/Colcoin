"""Сценарий клиента: жмёт кнопку -> выбирает пакеты -> вводит адрес -> заявка уходит."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import Config
from keyboards import bags_count_kb, courier_accept_kb, main_menu_kb
from pricing import calculate_price
from storage import create_order

router = Router(name="client")


class OrderFlow(StatesGroup):
    """Шаги пошагового диалога с клиентом."""

    waiting_for_address = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Привет! Я помогу вынести твой мусор.\n\n"
        "Нажми кнопку «🗑 Вынести мусор», чтобы оформить заявку.",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "🗑 Вынести мусор")
async def start_order(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Сколько пакетов нужно вынести?",
        reply_markup=bags_count_kb(),
    )


@router.callback_query(F.data.startswith("bags:"))
async def pick_bags(call: CallbackQuery, state: FSMContext) -> None:
    bags = int(call.data.split(":", 1)[1])
    price = calculate_price(bags)
    await state.update_data(bags=bags, price=price)
    await state.set_state(OrderFlow.waiting_for_address)
    await call.message.edit_text(
        f"Цена: <b>{price}₽</b> за {bags} пакет(а/ов).\n\n"
        "Теперь напиши адрес одним сообщением:\n"
        "<i>дом, квартира, окно</i>\n\n"
        "Например: <code>ул. Пушкина 10, кв. 25, окно справа во двор</code>",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(OrderFlow.waiting_for_address)
async def receive_address(message: Message, state: FSMContext, config: Config) -> None:
    address = (message.text or "").strip()
    if len(address) < 5:
        await message.answer("Адрес слишком короткий. Напиши подробнее: дом, квартира, окно.")
        return

    data = await state.get_data()
    bags = data["bags"]
    price = data["price"]

    order = create_order(
        client_chat_id=message.chat.id,
        client_username=message.from_user.username if message.from_user else None,
        bags=bags,
        price=price,
        address=address,
    )

    # Уведомление клиенту.
    await message.answer(
        f"✅ Заявка #{order.id} принята!\n\n"
        f"Пакетов: <b>{bags}</b>\n"
        f"К оплате: <b>{price}₽</b>\n"
        f"Адрес: {address}\n\n"
        "Курьер скоро придёт. Когда вынесет — пришлёт фото-отчёт сюда.",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
    await state.clear()

    # Отправка заявки курьеру.
    client_link = (
        f"@{order.client_username}"
        if order.client_username
        else f"<a href='tg://user?id={order.client_chat_id}'>клиент</a>"
    )
    courier_text = (
        f"🆕 Новая заявка #{order.id}\n\n"
        f"Пакетов: <b>{bags}</b>\n"
        f"Цена: <b>{price}₽</b>\n"
        f"Адрес: {address}\n"
        f"Клиент: {client_link}"
    )
    await message.bot.send_message(
        chat_id=config.courier_id,
        text=courier_text,
        parse_mode="HTML",
        reply_markup=courier_accept_kb(order.id),
    )

    # Копия админу.
    await message.bot.send_message(
        chat_id=config.admin_id,
        text=f"📋 Заявка #{order.id}\n\n{courier_text}",
        parse_mode="HTML",
    )


# ============================================================================
# TODO: ЗДЕСЬ БУДЕТ ОПЛАТА И АБОНЕМЕНТЫ
# ----------------------------------------------------------------------------
# Перед финальным сохранением заявки добавим:
#   1) Проверку остатка по абонементу "10 выносов" — если есть, цена 0₽,
#      consume_abonnement(user_id) уменьшает счётчик.
#   2) Иначе предложим оплату (Telegram Payments или ЮKassa-bot).
#   3) Заявка переходит в статус "оплачено" только после успешного платежа.
# Сейчас всё бесплатно и без оплаты — это MVP.
# ============================================================================
