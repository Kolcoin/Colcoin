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

## Фильтрация по ЖК или району

Например, оставить только сообщения про Митино или ЖК Алия:

```bash
python3 scripts/telegram_leads_parser.py result.json \
  --filter "митино" \
  --filter "жк алия" \
  --csv leads-filtered.csv
```

## Только новые сообщения

Для регулярного запуска используйте state-файл. Первый запуск сохранит обработанные сообщения, следующие запуски с `--only-new` выгрузят только новые лиды:

```bash
python3 scripts/telegram_leads_parser.py exports \
  --state data/telegram-leads-state.json \
  --only-new \
  --csv leads-new.csv
```

## Уведомления в Telegram

Создайте своего бота через `@BotFather`, получите token и узнайте chat ID, куда слать уведомления. Затем:

```bash
python3 scripts/telegram_leads_parser.py exports \
  --state data/telegram-leads-state.json \
  --only-new \
  --csv leads-new.csv \
  --notify-bot-token "123456:BOT_TOKEN" \
  --notify-chat-id "123456789"
```

Скрипт отправит краткое уведомление с первыми найденными лидами. Автоматически писать потенциальным клиентам в личку он не будет.

## Стартовый список публичных источников

Файл `config/telegram_newbuild_watchlist.json` содержит стартовый watchlist публичных каналов/чатов по новостройкам, ЖК и недвижимости Москвы.

Перед мониторингом проверьте правила каждого сообщества. Если чат запрещает сбор данных или рекламные ответы, не используйте его.

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
