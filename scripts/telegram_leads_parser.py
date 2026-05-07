from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_KEYWORDS = [
    "купить квартиру",
    "покупка квартиры",
    "квартиру купить",
    "квартира в жк",
    "квартиры в жк",
    "новостройка",
    "новостройки",
    "жк",
    "ипотека",
    "рассрочка",
    "бронь",
    "забронировать",
    "цена",
    "стоимость",
    "планировка",
    "отделка",
    "срок сдачи",
    "сдача дома",
    "метро",
]

NEGATIVE_KEYWORDS = [
    "снять",
    "сниму",
    "аренда",
    "сдаю",
    "сдам",
]


@dataclass(slots=True)
class Lead:
    chat_name: str
    message_id: int
    date: str
    sender: str
    sender_id: str
    score: int
    matched_keywords: list[str]
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chat_name": self.chat_name,
            "message_id": self.message_id,
            "date": self.date,
            "sender": self.sender,
            "sender_id": self.sender_id,
            "score": self.score,
            "matched_keywords": self.matched_keywords,
            "text": self.text,
        }


def normalize_message_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text", "")))
        return "".join(parts)
    return ""


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def score_text(text: str, keywords: list[str]) -> tuple[int, list[str]]:
    normalized = normalize_spaces(text.lower())
    matched = [keyword for keyword in keywords if keyword.lower() in normalized]
    score = len(matched)
    if any(keyword in normalized for keyword in NEGATIVE_KEYWORDS):
        score -= 1
    return score, matched


def iter_export_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.json")))
        elif path.is_file():
            files.append(path)
    return files


def parse_export(path: Path, keywords: list[str], min_score: int) -> list[Lead]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chat_name = str(data.get("name") or data.get("id") or path.stem)
    leads: list[Lead] = []

    for message in data.get("messages", []):
        if not isinstance(message, dict) or message.get("type") != "message":
            continue
        text = normalize_spaces(normalize_message_text(message.get("text")))
        if not text:
            continue
        score, matched = score_text(text, keywords)
        if score < min_score:
            continue
        leads.append(
            Lead(
                chat_name=chat_name,
                message_id=int(message.get("id") or 0),
                date=str(message.get("date") or ""),
                sender=str(message.get("from") or ""),
                sender_id=str(message.get("from_id") or ""),
                score=score,
                matched_keywords=matched,
                text=text,
            )
        )
    return leads


def write_csv(path: Path, leads: list[Lead]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "chat_name",
                "message_id",
                "date",
                "sender",
                "sender_id",
                "score",
                "matched_keywords",
                "text",
            ],
        )
        writer.writeheader()
        for lead in leads:
            row = lead.to_dict()
            row["matched_keywords"] = ", ".join(lead.matched_keywords)
            writer.writerow(row)


def write_json(path: Path, leads: list[Lead]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([lead.to_dict() for lead in leads], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Telegram Desktop JSON exports for new-building apartment buyer leads."
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Telegram JSON export files or directories")
    parser.add_argument("--csv", type=Path, default=Path("telegram-leads.csv"), help="CSV output path")
    parser.add_argument("--json", type=Path, help="Optional JSON output path")
    parser.add_argument("--keyword", action="append", default=[], help="Additional lead keyword")
    parser.add_argument("--min-score", type=int, default=1, help="Minimum keyword score")
    args = parser.parse_args()

    keywords = DEFAULT_KEYWORDS + [item.strip() for item in args.keyword if item.strip()]
    leads: list[Lead] = []
    for export_file in iter_export_files(args.paths):
        leads.extend(parse_export(export_file, keywords, args.min_score))

    leads.sort(key=lambda lead: (lead.date, lead.score), reverse=True)
    write_csv(args.csv, leads)
    if args.json:
        write_json(args.json, leads)

    print(f"Found {len(leads)} leads")
    print(f"CSV: {args.csv}")
    if args.json:
        print(f"JSON: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
