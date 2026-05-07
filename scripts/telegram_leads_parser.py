from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


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

BUYER_INTENT_PATTERNS = [
    r"\bхочу\b.{0,80}\b(купить|взять|приобрести|забронировать)\b",
    r"\bищу\b.{0,80}\b(квартир|новостро|жк|студи|двуш|однуш)",
    r"\bинтересует\b.{0,80}\b(квартир|новостро|жк|ипотек|цен|стоимост|планиров)",
    r"\bподскажите\b.{0,100}\b(цен|стоимост|ипотек|квартир|жк|новостро|брон)",
    r"\bкакая\b.{0,40}\b(цена|стоимость)\b",
    r"\bсколько\b.{0,60}\b(стоит|стоимость|цена)\b",
    r"\bможно\b.{0,80}\b(забронировать|купить|посмотреть|оформить)\b",
    r"\bнужна\b.{0,80}\b(квартир|новостро|ипотек|двуш|однуш|студи)",
    r"\bрассматриваю\b.{0,80}\b(квартир|новостро|жк|покупк)",
    r"\bпланирую\b.{0,80}\b(покуп|купить|взять|ипотек)",
]

REAL_ESTATE_CONTEXT = [
    "квартир",
    "новостро",
    "жк",
    "ипотек",
    "студи",
    "однуш",
    "двуш",
    "треш",
    "апартамент",
    "метро",
]

POST_LIKE_KEYWORDS = [
    "итоги года",
    "новые правила",
    "почему дорожают",
    "эксперты",
    "аналитика",
    "подборка",
    "топ-",
    "рейтинг",
    "банк предлож",
    "застройщик объявил",
    "старт продаж",
    "акция от",
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


def has_buyer_intent(text: str) -> bool:
    normalized = normalize_spaces(text.lower())
    has_intent = any(re.search(pattern, normalized) for pattern in BUYER_INTENT_PATTERNS)
    has_context = any(keyword in normalized for keyword in REAL_ESTATE_CONTEXT)
    looks_like_post = any(keyword in normalized for keyword in POST_LIKE_KEYWORDS)
    return has_intent and has_context and not looks_like_post


def score_text(text: str, keywords: list[str], strict_buyer: bool = True) -> tuple[int, list[str]]:
    normalized = normalize_spaces(text.lower())
    if strict_buyer and not has_buyer_intent(normalized):
        return 0, []
    matched = [keyword for keyword in keywords if keyword.lower() in normalized]
    intent_bonus = 3 if has_buyer_intent(normalized) else 0
    score = len(matched) + intent_bonus
    if any(keyword in normalized for keyword in NEGATIVE_KEYWORDS):
        score -= 3
    return score, matched


def iter_export_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.json")))
        elif path.is_file():
            files.append(path)
    return files


def parse_export(path: Path, keywords: list[str], min_score: int, strict_buyer: bool = True) -> list[Lead]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chat_name = str(data.get("name") or data.get("id") or path.stem)
    leads: list[Lead] = []

    for message in data.get("messages", []):
        if not isinstance(message, dict) or message.get("type") != "message":
            continue
        text = normalize_spaces(normalize_message_text(message.get("text")))
        if not text:
            continue
        score, matched = score_text(text, keywords, strict_buyer=strict_buyer)
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


def load_state(path: Path | None) -> dict[str, int]:
    if not path or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(key): int(value) for key, value in data.items()}


def save_state(path: Path | None, leads: list[Lead], previous_state: dict[str, int]) -> None:
    if not path:
        return
    state = dict(previous_state)
    for lead in leads:
        state[lead.chat_name] = max(state.get(lead.chat_name, 0), lead.message_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def filter_new_leads(leads: list[Lead], state: dict[str, int]) -> list[Lead]:
    return [lead for lead in leads if lead.message_id > state.get(lead.chat_name, 0)]


def filter_by_terms(leads: list[Lead], terms: list[str]) -> list[Lead]:
    normalized_terms = [term.lower() for term in terms if term.strip()]
    if not normalized_terms:
        return leads
    result: list[Lead] = []
    for lead in leads:
        text = lead.text.lower()
        if any(term in text for term in normalized_terms):
            result.append(lead)
    return result


def send_telegram_notification(bot_token: str, chat_id: str, leads: list[Lead]) -> None:
    if not leads:
        return
    preview = leads[:10]
    lines = [f"Найдено лидов: {len(leads)}"]
    for lead in preview:
        lines.append(
            f"• {lead.sender or lead.sender_id} | {lead.chat_name} | score {lead.score}\n"
            f"{lead.text[:250]}"
        )
    if len(leads) > len(preview):
        lines.append(f"Еще {len(leads) - len(preview)} лидов в CSV.")

    payload = urlencode(
        {
            "chat_id": chat_id,
            "text": "\n\n".join(lines),
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=payload,
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        response.read()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Telegram Desktop JSON exports for new-building apartment buyer leads."
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Telegram JSON export files or directories")
    parser.add_argument("--csv", type=Path, default=Path("telegram-leads.csv"), help="CSV output path")
    parser.add_argument("--json", type=Path, help="Optional JSON output path")
    parser.add_argument("--keyword", action="append", default=[], help="Additional lead keyword")
    parser.add_argument("--filter", action="append", default=[], help="Keep only leads containing this ЖК/район term")
    parser.add_argument("--min-score", type=int, default=1, help="Minimum keyword score")
    parser.add_argument("--broad", action="store_true", help="Broad keyword mode; includes posts/news, not recommended for leads")
    parser.add_argument("--state", type=Path, help="State file for incremental runs")
    parser.add_argument("--only-new", action="store_true", help="Export only messages newer than state")
    parser.add_argument("--notify-bot-token", help="Telegram bot token for lead notifications")
    parser.add_argument("--notify-chat-id", help="Telegram chat ID for lead notifications")
    args = parser.parse_args()

    keywords = DEFAULT_KEYWORDS + [item.strip() for item in args.keyword if item.strip()]
    state = load_state(args.state)
    leads: list[Lead] = []
    for export_file in iter_export_files(args.paths):
        leads.extend(parse_export(export_file, keywords, args.min_score, strict_buyer=not args.broad))

    if args.only_new:
        leads = filter_new_leads(leads, state)
    leads = filter_by_terms(leads, args.filter)
    leads.sort(key=lambda lead: (lead.date, lead.score), reverse=True)
    write_csv(args.csv, leads)
    if args.json:
        write_json(args.json, leads)
    save_state(args.state, leads, state)
    if args.notify_bot_token and args.notify_chat_id:
        send_telegram_notification(args.notify_bot_token, args.notify_chat_id, leads)

    print(f"Found {len(leads)} leads")
    print(f"CSV: {args.csv}")
    if args.json:
        print(f"JSON: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
