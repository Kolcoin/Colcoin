# Telegram Managed Bots MVP (Training Scaffold)

This repository now contains a practical, safe-by-default scaffold for learning Telegram
Managed Bots workflows with placeholder values only.

> Never commit real bot tokens or API keys.

## What's included

- `managed_bots/`:
  - `config.py`: secure environment loading with secret-leak guardrails.
  - `events.py`: typed event payloads for managed bot creation and user messages.
  - `storage.py`: in-memory repository simulating encrypted-token storage.
  - `links.py`: helper to generate managed bot creation links.
  - `service.py`: orchestration layer for:
    - bot creation events (`on_managed_bot_created`)
    - managed bot user messages (`on_managed_bot_message`)
  - `ai_client.py`: OpenRouter-style integration helper with placeholder key support.
- `sql/managed_bots.sql`: starter schema for `managed_bots` + `managed_bot_messages`.
- `tests/test_managed_bots.py`: async tests with mocks and placeholders.
- `.env.example`: safe environment template.
- `.gitignore`: ignores local secrets, env files, and virtualenv artifacts.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set placeholders in your local `.env` (not committed), then run tests:

```bash
pytest
```

## Daily Telegram autoposter

There is a ready-to-run daily autoposter scaffold in `autoposter/`.

Docs:

- `docs/TELEGRAM_AUTOPOSTER.md`

Run one post manually:

```bash
python3 scripts/run_daily_post.py --dry-run
```

Moderation worker (approve/reject in personal chat):

```bash
python3 scripts/run_moderation_worker.py --once
```

Run moderation worker (approve/reject in private chat):

```bash
python3 scripts/run_moderation_worker.py
```

## Security notes

- Required tokens and keys are loaded only from environment variables.
- `load_config` rejects obvious real-token patterns in this training scaffold.
- Any persistent token storage must be encrypted before writing to DB.

## Managed Bot creation link example

```python
from managed_bots.links import generate_bot_creation_link

link = generate_bot_creation_link(
    management_bot_username="YOUR_BOT_USERNAME",
    desired_bot_username="pleada_ai_ivan_123",
    desired_bot_name="PLEADA AI - Ivan Petrov",
)
print(link)
```

## Checklist for MVP

- [ ] Management Bot configured in BotFather (`Bot Management Mode -> ON`)
- [ ] Environment variables configured locally (placeholders replaced)
- [ ] Managed bot creation event handler wired to real telegram update source
- [ ] Managed bot message handler wired to real updates
- [ ] Database schema applied
- [ ] AI response integration configured
- [ ] Token encryption and key rotation policy implemented
