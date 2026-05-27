from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.telegram_leads_parser import (
    DEFAULT_KEYWORDS,
    filter_by_terms,
    filter_new_leads,
    parse_export,
    save_state,
    write_csv,
)


class TelegramLeadsParserTest(unittest.TestCase):
    def test_extracts_apartment_purchase_leads_from_export(self) -> None:
        with TemporaryDirectory() as tmp:
            export = Path(tmp) / "result.json"
            export.write_text(
                json.dumps(
                    {
                        "name": "Новостройки Москвы",
                        "messages": [
                            {
                                "id": 1,
                                "type": "message",
                                "date": "2026-05-07T10:00:00",
                                "from": "Алексей",
                                "from_id": "user123",
                                "text": "Интересует покупка квартиры в ЖК Примавера, какая цена?",
                            },
                            {
                                "id": 2,
                                "type": "message",
                                "date": "2026-05-07T10:05:00",
                                "from": "Мария",
                                "from_id": "user456",
                                "text": [
                                    "Можно ",
                                    {"type": "bold", "text": "забронировать"},
                                    " новостройку рядом с метро?",
                                ],
                            },
                            {
                                "id": 3,
                                "type": "message",
                                "date": "2026-05-07T10:10:00",
                                "from": "Иван",
                                "from_id": "user789",
                                "text": "Сниму квартиру, нужна аренда.",
                            },
                            {
                                "id": 4,
                                "type": "message",
                                "date": "2026-05-07T10:15:00",
                                "from": "Новостройки Москвы",
                                "from_id": "channel1",
                                "text": "Итоги года: почему дорожают новостройки и что говорят эксперты.",
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            leads = parse_export(export, DEFAULT_KEYWORDS, min_score=1)
            self.assertEqual([lead.sender for lead in leads], ["Алексей", "Мария"])
            self.assertIn("покупка квартиры", leads[0].matched_keywords)
            self.assertIn("забронировать", leads[1].text)

            csv_path = Path(tmp) / "leads.csv"
            write_csv(csv_path, leads)
            with csv_path.open(encoding="utf-8-sig", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(rows[0]["sender"], "Алексей")
            self.assertEqual(rows[0]["chat_name"], "Новостройки Москвы")

    def test_filters_by_term_and_tracks_new_messages(self) -> None:
        with TemporaryDirectory() as tmp:
            export = Path(tmp) / "result.json"
            export.write_text(
                json.dumps(
                    {
                        "name": "Покупка квартир",
                        "messages": [
                            {
                                "id": 10,
                                "type": "message",
                                "date": "2026-05-07T11:00:00",
                                "from": "Анна",
                                "from_id": "user10",
                                "text": "Ищу новостройку в Митино, интересует ипотека.",
                            },
                            {
                                "id": 11,
                                "type": "message",
                                "date": "2026-05-07T11:10:00",
                                "from": "Сергей",
                                "from_id": "user11",
                                "text": "Хочу купить квартиру в ЖК Алия.",
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            leads = parse_export(export, DEFAULT_KEYWORDS, min_score=1)
            mitino = filter_by_terms(leads, ["митино"])
            self.assertEqual([lead.sender for lead in mitino], ["Анна"])

            state_path = Path(tmp) / "state.json"
            save_state(state_path, [leads[0]], {})
            new_leads = filter_new_leads(leads, {"Покупка квартир": 10})
            self.assertEqual([lead.sender for lead in new_leads], ["Сергей"])


if __name__ == "__main__":
    unittest.main()
