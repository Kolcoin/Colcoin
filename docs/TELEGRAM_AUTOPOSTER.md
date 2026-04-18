# Telegram Autoposter (1 post/day)

This setup gives you a practical pipeline:
- generate one post with OpenRouter
- moderation mode: send draft to your personal Telegram first
- publish to channel only after explicit approval
- run daily by cron + lightweight moderation worker
- avoid repetitive topics using local JSON state

## 1) Prepare Telegram access

1. Create bot in `@BotFather` via `/newbot`
2. Save `TELEGRAM_BOT_TOKEN` safely (never commit to git)
3. Add bot to channel as admin with post permissions
4. Set `TELEGRAM_CHANNEL_ID`
   - public channel: `@channel_name`
   - private channel: `-1001234567890`

## 2) Configure `.env`

```bash
cp .env.example .env
```

Fill required values:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`
- `OPENROUTER_API_KEY`

Recommended fields:
- `OPENROUTER_MODEL` (default: `openai/gpt-4o-mini`)
- `OPENROUTER_REFERER`
- `AUTOPOSTER_CONTACT_HANDLE` (for CTA line)
- `AUTOPOSTER_TOPICS` (semicolon-separated themes, e.g. `тема1;тема2;тема3`)
- `AUTOPOSTER_STATE_FILE` (default: `.autoposter_state.json`)
- `AUTOPOSTER_ENABLE_MODERATION=true`
- `AUTOPOSTER_REVIEWER_CHAT_ID=<your personal chat id>`

## 3) Install deps

```bash
python3 -m pip install -r requirements.txt
```

## 4) Dry run (no publish)

```bash
python3 -m autoposter.cli --dry-run
```

## 5) Publish one post manually

```bash
python3 -m autoposter.cli
```

If moderation mode is enabled, this command sends draft to your personal chat
with buttons:
- `Опубликовать`
- `Отклонить`

The channel receives post only after `Опубликовать`.

## 6) Daily scheduler via cron

Open cron:

```bash
crontab -e
```

Add two jobs:

1) Daily generation (example: every day at 10:00):

```cron
0 10 * * * cd /workspace && /usr/bin/python3 scripts/run_daily_post.py >> /workspace/autoposter.log 2>&1
```

2) Moderation worker (polls Telegram updates and applies approve/reject):

```cron
* * * * * cd /workspace && /usr/bin/python3 scripts/run_moderation_worker.py --moderation-worker >> /workspace/autoposter-moderation.log 2>&1
```

## 7) How anti-duplication works

- Script keeps recent history in `AUTOPOSTER_STATE_FILE`
- It avoids picking the same topic as the latest publication
- Each run writes date, topic, and short preview
- Pending moderation drafts are also stored in state JSON until approved/rejected

## Security rules

- Never commit `.env`
- Never store real tokens in docs or source
- Rotate keys if they were ever exposed

