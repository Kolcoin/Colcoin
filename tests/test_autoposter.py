from pathlib import Path

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
