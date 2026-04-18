"""State helpers for deduplication and posting history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class StateStore:
    """Simple JSON-backed state for autoposter runtime."""

    def __init__(self, state_path: str) -> None:
        self._path = Path(state_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[dict[str, str]]:
        if not self._path.exists():
            return []
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        result: list[dict[str, str]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            result.append(
                {
                    "date": str(item.get("date", "")),
                    "topic": str(item.get("topic", "")),
                    "message_preview": str(item.get("message_preview", "")),
                }
            )
        return result

    def append(self, topic: str, text: str) -> None:
        items = self.load()
        items.append(
            {
                "date": datetime.now(timezone.utc).date().isoformat(),
                "topic": topic,
                "message_preview": " ".join(text.split())[:120],
            }
        )
        self._path.write_text(
            json.dumps(items[-90:], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
