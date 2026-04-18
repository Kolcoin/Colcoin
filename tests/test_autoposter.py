from pathlib import Path

from autoposter.moderation import ACTION_APPROVE, build_keyboard, parse_callback_data
from autoposter.runner import choose_topic
from autoposter.state import StateStore


def test_choose_topic_skips_recent() -> None:
    selected = choose_topic(
        topics=["analytics", "offer", "tips"],
        recent=["analytics"],
    )
    assert selected in {"offer", "tips"}


def test_state_store_roundtrip(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"
    store = StateStore(str(state_file))
    store.append(topic="offer", text="preview text")
    payload = store.load()
    assert len(payload) == 1
    assert payload[0]["topic"] == "offer"


def test_state_store_pending_roundtrip(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"
    store = StateStore(str(state_file))
    token = "token123"
    store.save_pending(
        token=token,
        topic="analytics",
        text="pending text",
        reviewer_chat_id="12345",
        review_message_id=77,
    )
    pending = store.get_pending(token)
    assert pending is not None
    assert pending["topic"] == "analytics"
    assert pending["review_message_id"] == 77
    removed = store.remove_pending(token)
    assert removed is not None
    assert store.get_pending(token) is None


def test_moderation_callback_parsing_roundtrip() -> None:
    keyboard = build_keyboard(token="token123")
    data = keyboard["inline_keyboard"][0][0]["callback_data"]
    parsed = parse_callback_data(data)
    assert parsed is not None
    action, token = parsed
    assert action == ACTION_APPROVE
    assert token == "token123"
