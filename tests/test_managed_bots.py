import pytest

from managed_bots.config import SecurityError, load_config
from managed_bots.events import ManagedBotEvent, ManagedBotInfo, ManagedBotOwner, UserMessageEvent
from managed_bots.links import create_customer_bot_link, generate_bot_creation_link
from managed_bots.service import ManagedBotService
from managed_bots.storage import InMemoryStorage


def test_generate_bot_creation_link_url_encodes_name() -> None:
    link = generate_bot_creation_link(
        management_bot_username="YOUR_BOT_USERNAME",
        desired_bot_username="pleada_ai_ivan_123",
        desired_bot_name="PLEADA AI — Ivan Petrov",
    )
    assert link.startswith("https://t.me/newbot/YOUR_BOT_USERNAME/pleada_ai_ivan_123")
    assert "name=PLEADA%20AI%20%E2%80%94%20Ivan%20Petrov" in link


def test_create_customer_bot_link_normalizes_username() -> None:
    link = create_customer_bot_link(
        customer_name="Ivan Petrov",
        customer_id=42,
        management_bot_username="pleada_bot",
    )
    assert link.startswith("https://t.me/newbot/pleada_bot/pleada_ai_customer_42")


def test_load_config_rejects_placeholders(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_MANAGEMENT_BOT_TOKEN", "YOUR_MANAGEMENT_BOT_TOKEN_HERE")
    monkeypatch.setenv("TELEGRAM_MANAGEMENT_BOT_USERNAME", "YOUR_BOT_USERNAME")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-YOUR_KEY_HERE")
    with pytest.raises(SecurityError):
        load_config()


@pytest.mark.asyncio
async def test_on_managed_bot_created_stores_bot_and_sends_welcome() -> None:
    storage = InMemoryStorage()
    service = ManagedBotService(storage=storage)
    event = ManagedBotEvent(
        managed_bot=ManagedBotInfo(
            bot=ManagedBotOwner(id=9999999999, username="test_bot_123"),
            user_id=111111111,
        )
    )

    token_calls: list[tuple[int, int]] = []
    welcome_calls: list[tuple[int, str, str]] = []

    async def fake_get_token(user_id: int, bot_id: int) -> str:
        token_calls.append((user_id, bot_id))
        return "1234567890:TRAINING_ONLY_MANAGED_TOKEN"

    async def fake_send_message(bot_token: str, user_id: int, text: str) -> None:
        welcome_calls.append((user_id, bot_token, text))

    await service.on_managed_bot_created(
        event,
        get_managed_bot_token=fake_get_token,
        send_message=fake_send_message,
    )
    assert token_calls == [(111111111, 9999999999)]
    assert len(welcome_calls) == 1
    assert welcome_calls[0][0] == 111111111
    assert "TRAINING_ONLY_MANAGED_TOKEN" in welcome_calls[0][1]
    assert "создан" in welcome_calls[0][2].lower()
    assert storage.bots[9999999999].owner_id == 111111111


@pytest.mark.asyncio
async def test_on_managed_bot_message_logs_and_returns_ai_reply() -> None:
    storage = InMemoryStorage()
    service = ManagedBotService(storage=storage)
    storage.save_bot(
        bot_id=7777777777,
        bot_username="demo_bot",
        owner_id=222222222,
        token_encrypted="enc::token",
    )

    event = UserMessageEvent(
        managed_bot_id=7777777777,
        user_id=222222222,
        text="Есть ли студии с балконом?",
    )

    async def fake_process_with_ai(text: str, context: dict[str, int]) -> str:
        assert text == "Есть ли студии с балконом?"
        assert context["managed_bot_id"] == 7777777777
        assert context["user_id"] == 222222222
        return "Да, есть несколько вариантов в центре."

    sent_messages: list[tuple[int, int, str]] = []

    async def fake_send_reply(managed_bot_id: int, user_id: int, text: str) -> None:
        sent_messages.append((managed_bot_id, user_id, text))

    answer = await service.on_managed_bot_message(
        event,
        process_with_ai=fake_process_with_ai,
        send_reply=fake_send_reply,
    )
    assert answer == "Да, есть несколько вариантов в центре."
    assert sent_messages == [(7777777777, 222222222, "Да, есть несколько вариантов в центре.")]
    assert len(storage.messages) == 1
    assert storage.messages[0].user_message == "Есть ли студии с балконом?"
