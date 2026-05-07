# Парсер лидов из Telegram-чатов

Скрипт анализирует JSON-экспорт Telegram-чата и находит сообщения, где люди интересуются покупкой квартиры, новостройками, ЖК, ипотекой, ценой, бронью и похожими темами.

Важно: используйте только чаты, к которым у вас есть законный доступ и право обработки данных. Скрипт не взламывает Telegram, не обходит приватность и не парсит закрытые чаты без доступа.

## Как получить экспорт Telegram

1. Откройте Telegram Desktop.
2. Зайдите в нужный чат или группу.
3. Нажмите меню чата.
4. Выберите `Export chat history`.
5. Формат экспорта: `JSON`.
6. Сохраните файл `result.json`.

## Запуск

```bash
python3 scripts/telegram_leads_parser.py /path/to/result.json --csv leads.csv --json leads.json
```

Можно передать папку с несколькими JSON-файлами:

```bash
python3 scripts/telegram_leads_parser.py /path/to/exports --csv leads.csv
```

## Дополнительные ключевые слова

```bash
python3 scripts/telegram_leads_parser.py result.json --keyword "жк алия" --keyword "новостройки митино"
```

## Что будет в CSV

- `chat_name` — название чата;
- `message_id` — ID сообщения;
- `date` — дата;
- `sender` — автор сообщения;
- `sender_id` — ID автора из экспорта Telegram;
- `score` — количество найденных признаков интереса;
- `matched_keywords` — найденные ключевые слова;
- `text` — текст сообщения.

## Пример использования для новостроек

```bash
python3 scripts/telegram_leads_parser.py result.json \
  --keyword "купить квартиру в новостройке" \
  --keyword "жк примавера" \
  --keyword "жк алия" \
  --csv leads.csv
```
