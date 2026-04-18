"""Moderation mode helpers for Telegram autoposter."""

from __future__ import annotations

from .config import load_autoposter_config
from .state import StateStore
from .telegram_publisher import TelegramBotApi

ACTION_APPROVE = "approve"
ACTION_REJECT = "reject"


def encode_callback_data(action: str, token: str) -> str:
    """Encode callback data for Telegram button."""
    return f"m|{action}|{token}"


def parse_callback_data(data: str) -> tuple[str, str] | None:
    """Parse callback data and return (action, token)."""
    parts = data.split("|", 2)
    if len(parts) != 3 or parts[0] != "m":
        return None
    _, action, token = parts
    if action not in {ACTION_APPROVE, ACTION_REJECT}:
        return None
    return action, token


def build_moderation_message(*, topic: str, post_text: str) -> str:
    """Construct moderation preview message for reviewer."""
    return (
        "📝 <b>Пост на согласование</b>\n\n"
        f"<b>Тема:</b> {topic}\n\n"
        f"{post_text}\n\n"
        "Выберите действие ниже:"
    )


def build_keyboard(*, token: str) -> dict:
    """Build inline keyboard payload for approve/reject actions."""
    return {
        "inline_keyboard": [
            [
                {"text": "✅ Опубликовать", "callback_data": encode_callback_data(ACTION_APPROVE, token)},
                {"text": "❌ Отклонить", "callback_data": encode_callback_data(ACTION_REJECT, token)},
            ]
        ]
    }


async def send_for_moderation(
    *,
    config,
    state: StateStore,
    topic: str,
    post_text: str,
) -> str:
    """Send draft post to reviewer chat and persist pending token."""
    token = state.save_pending(
        topic=topic,
        text=post_text,
        reviewer_chat_id=config.moderation_chat_id,
        review_message_id=0,
    )
    bot = TelegramBotApi(config.telegram_bot_token)
    sent = await bot.send_message(
        chat_id=config.moderation_chat_id,
        text=build_moderation_message(topic=topic, post_text=post_text),
        reply_markup=build_keyboard(token=token),
    )
    sent_message = sent.get("result", {})
    state.update_pending_message_meta(
        token=token,
        review_chat_id=config.moderation_chat_id,
        review_message_id=int(sent_message.get("message_id", 0)),
    )
    return token


async def run_moderation_worker() -> None:
    """Process one batch of moderation callback updates."""
    config = load_autoposter_config()
    bot = TelegramBotApi(config.telegram_bot_token)
    state = StateStore(config.state_file)
    last_update_id = state.get_worker_offset()
    updates = await bot.get_updates(offset=last_update_id + 1, timeout=0)
    max_seen = last_update_id

    for update in updates:
        update_id = int(update.get("update_id", 0))
        if update_id > max_seen:
            max_seen = update_id

        callback = update.get("callback_query")
        if not isinstance(callback, dict):
            continue

        callback_id = str(callback.get("id", ""))
        data = str(callback.get("data", ""))
        parsed = parse_callback_data(data)
        if not parsed:
            if callback_id:
                await bot.answer_callback_query(
                    callback_query_id=callback_id,
                    text="Неизвестная команда.",
                    show_alert=False,
                )
            continue

        action, token = parsed
        pending = state.get_pending(token)
        if not pending:
            if callback_id:
                await bot.answer_callback_query(
                    callback_query_id=callback_id,
                    text="Черновик уже обработан.",
                    show_alert=True,
                )
            continue

        message_obj = callback.get("message", {})
        review_message_id = int(message_obj.get("message_id", 0))
        review_chat = message_obj.get("chat", {})
        review_chat_id = str(review_chat.get("id", pending.get("reviewer_chat_id", "")))

        if action == ACTION_APPROVE:
            await bot.send_message(
                chat_id=config.telegram_channel_id,
                text=str(pending.get("text", "")),
            )
            state.append(
                topic=str(pending.get("topic", "")),
                text=str(pending.get("text", "")),
            )
            decision_text = "✅ Опубликовано в канал."
        else:
            decision_text = "❌ Отклонено. В канал не отправлено."

        state.remove_pending(token)

        if review_message_id > 0 and review_chat_id:
            await bot.edit_message_reply_markup(
                chat_id=review_chat_id,
                message_id=review_message_id,
                reply_markup={"inline_keyboard": []},
            )

        if callback_id:
            await bot.answer_callback_query(
                callback_query_id=callback_id,
                text=decision_text,
                show_alert=False,
            )

    state.set_worker_offset(max_seen)
