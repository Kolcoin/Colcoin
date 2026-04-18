"""State helpers for deduplication and moderation flow."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class StateStore:
    """JSON-backed storage for published posts and moderation drafts."""

    def __init__(self, state_path: str) -> None:
        self._path = Path(state_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[dict[str, str]]:
        payload = self._read()
        published = payload.get("published", [])
        if not isinstance(published, list):
            return []
        result: list[dict[str, str]] = []
        for item in published:
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
        payload = self._read()
        published = payload.get("published", [])
        if not isinstance(published, list):
            published = []
        published.append(
            {
                "date": datetime.now(timezone.utc).date().isoformat(),
                "topic": topic,
                "message_preview": " ".join(text.split())[:120],
            }
        )
        payload["published"] = published[-90:]
        self._write(payload)

    def recent_topics(self, limit: int = 2) -> list[str]:
        if limit <= 0:
            return []
        return [item["topic"] for item in self.load()[-limit:] if item.get("topic")]

    def save_pending(
        self,
        *,
        token: str,
        topic: str,
        text: str,
        reviewer_chat_id: str,
        review_message_id: int,
    ) -> None:
        payload = self._read()
        pending = payload.get("pending", {})
        if not isinstance(pending, dict):
            pending = {}
        pending[token] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "topic": topic,
            "text": text,
            "reviewer_chat_id": reviewer_chat_id,
            "review_message_id": review_message_id,
        }
        payload["pending"] = pending
        self._write(payload)

    def get_pending(self, token: str) -> dict[str, Any] | None:
        payload = self._read()
        pending = payload.get("pending", {})
        if not isinstance(pending, dict):
            return None
        item = pending.get(token)
        if isinstance(item, dict):
            return item
        return None

    def remove_pending(self, token: str) -> dict[str, Any] | None:
        payload = self._read()
        pending = payload.get("pending", {})
        if not isinstance(pending, dict):
            return None
        item = pending.pop(token, None)
        payload["pending"] = pending
        self._write(payload)
        if isinstance(item, dict):
            return item
        return None

    def get_worker_offset(self) -> int:
        payload = self._read()
        offset = payload.get("worker_offset", 0)
        try:
            return int(offset)
        except (TypeError, ValueError):
            return 0

    def set_worker_offset(self, value: int) -> None:
        payload = self._read()
        payload["worker_offset"] = int(value)
        self._write(payload)

    def _read(self) -> dict[str, Any]:
        if not self._path.exists():
            return {"published": [], "pending": {}, "worker_offset": 0}
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return {"published": [], "pending": {}, "worker_offset": 0}
        raw.setdefault("published", [])
        raw.setdefault("pending", {})
        raw.setdefault("worker_offset", 0)
        return raw

    def _write(self, payload: dict[str, Any]) -> None:
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
