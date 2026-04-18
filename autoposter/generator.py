"""Content generation via OpenRouter-compatible API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from .config import AutoposterConfig
from .templates.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def _build_bullet_points(topic: str) -> list[str]:
    return [
        f"Ключевой фокус дня: {topic}",
        "Сравнить 2-3 сценария покупки: ипотека, рассрочка, 100% оплата",
        "Проверить ликвидность лота: этаж, вид, планировка, срок ввода",
    ]


async def generate_post(
    *,
    config: AutoposterConfig,
    topic: str,
) -> str:
    """Generate one channel post text in configured style."""
    bullet_points = _build_bullet_points(topic)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        rubric=topic,
        today=datetime.now().strftime("%Y-%m-%d"),
        topic=topic,
        bullet_points="\n".join(f"- {point}" for point in bullet_points),
        contact_handle=config.contact_handle,
    )

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(
            url=config.openrouter_base_url,
            headers={
                "Authorization": f"Bearer {config.openrouter_api_key}",
                "HTTP-Referer": config.openrouter_referer,
                "X-Title": "telegram-autoposter",
            },
            json={
                "model": config.openrouter_model,
                "temperature": config.generation_temperature,
                "max_tokens": config.generation_max_tokens,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            },
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
    return payload["choices"][0]["message"]["content"].strip()
