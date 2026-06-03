"""Сценарий курьера: кнопка «Выполнено #N» → бот ждёт фото → фото уходит клиенту и в группу."""

from maxapi import CallbackData, Router, State, StateFilter, StatesGroup

from config import Config
from storage import get_order, set_status

router = Router()


class CourierFlow(StatesGroup):
    waiting_photo = State()


@router.callback_handler(CallbackData("done:", startswith=True))
async def on_done(event, state):
    config: Config = event.bot._config

    if event.user_id != config.courier_id:
        await event.bot.answer_callback(
            event.callback_id,
            notification="Эта кнопка только для курьера",
        )
        return

    order_id = int(event.payload_text.split(":", 1)[1])
    order = get_order(order_id)
    if order is None:
        await event.bot.answer_callback(event.callback_id, notification="Заказ не найден")
        return

    set_status(order_id, "waiting_photo")
    await state.set_state(CourierFlow.waiting_photo)
    await state.update_data(active_order_id=order_id)
    await event.bot.answer_callback(event.callback_id)
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="📸 Пришли фото выполненного заказа следующим сообщением.",
    )


@router.message_created(StateFilter(CourierFlow.waiting_photo))
async def on_photo(event, state):
    config: Config = event.bot._config

    if event.user_id != config.courier_id:
        return

    images = event.message.images
    if not images:
        await event.message.answer("Жду фото. Пришли картинку, не текст.")
        return

    data = await state.get_data()
    order_id = data.get("active_order_id")
    order = get_order(order_id) if order_id else None
    if order is None:
        await event.message.answer("Не вижу активного заказа. Открой заказ ещё раз.")
        await state.clear()
        return

    # Пересылаем фото — берём первый attachment и шлём его как image-attachment.
    photo_attachment = event.message.attachments[0]
    forward = [photo_attachment]

    # Клиенту.
    await event.bot.send_message(
        chat_id=order.client_chat_id,
        text=f"✅ Заказ #{order.id} закрыт. Спасибо, что выбрал нас! 😊",
        attachments=forward,
    )

    # В группу — отчёт.
    await event.bot.send_message(
        chat_id=config.group_id,
        text=f"✅ Заказ #{order.id} ВЫПОЛНЕН\n🏠 {order.address}",
        attachments=forward,
    )

    set_status(order_id, "done")
    await state.clear()
    await event.message.answer(f"Принято! Заказ #{order.id} закрыт. 💪")
