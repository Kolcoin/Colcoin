"""Сценарий курьера: принимает заявку кнопкой, потом шлёт фото — оно уходит клиенту и админу."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import Config
from storage import get_order, mark_done, mark_in_progress

router = Router(name="courier")


class CourierFlow(StatesGroup):
    """Когда курьер принял заказ — он в этом состоянии. Следующее фото = отчёт."""

    waiting_photo = State()


def _is_courier(event_user_id: int, config: Config) -> bool:
    return event_user_id == config.courier_id


@router.callback_query(F.data.startswith("accept:"))
async def accept_order(call: CallbackQuery, state: FSMContext, config: Config) -> None:
    if not _is_courier(call.from_user.id, config):
        await call.answer("Эта кнопка только для курьера.", show_alert=True)
        return

    order_id = int(call.data.split(":", 1)[1])
    order = mark_in_progress(order_id, courier_chat_id=call.from_user.id)
    if order is None:
        await call.answer("Заказ не найден.", show_alert=True)
        return

    await state.set_state(CourierFlow.waiting_photo)
    await state.update_data(active_order_id=order_id)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        f"Заказ #{order_id} принят. Когда вынесешь — пришли фото следующим сообщением."
    )
    await call.answer("Заказ принят")


@router.message(CourierFlow.waiting_photo, F.photo)
async def receive_photo(message: Message, state: FSMContext, config: Config) -> None:
    if not _is_courier(message.from_user.id, config):
        return

    data = await state.get_data()
    order_id = data.get("active_order_id")
    if order_id is None:
        await message.answer("Не вижу активного заказа. Сначала прими заявку кнопкой.")
        await state.clear()
        return

    order = get_order(order_id)
    if order is None:
        await message.answer("Заказ не найден.")
        await state.clear()
        return

    photo_file_id = message.photo[-1].file_id

    # Фото клиенту.
    await message.bot.send_photo(
        chat_id=order.client_chat_id,
        photo=photo_file_id,
        caption=f"✅ Заказ #{order.id} выполнен. Спасибо, что выбрали нас!",
    )

    # Фото админу.
    await message.bot.send_photo(
        chat_id=config.admin_id,
        photo=photo_file_id,
        caption=f"📸 Заказ #{order.id} выполнен курьером.",
    )

    mark_done(order_id)
    await state.clear()
    await message.answer("Фото отправлено клиенту и админу. Спасибо!")


@router.message(CourierFlow.waiting_photo)
async def waiting_for_photo_but_got_text(message: Message) -> None:
    """Если курьер вместо фото написал текст — напомним."""
    if message.text and message.text.startswith("/"):
        return  # пропускаем команды
    await message.answer("Жду фото мусора. Пришли картинку, не текст.")
