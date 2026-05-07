from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.telegram_leads_parser import DEFAULT_KEYWORDS, parse_export, write_csv


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


if __name__ == "__main__":
    unittest.main()
