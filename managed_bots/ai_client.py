"""Minimal AI client adapter using OpenRouter-style API."""

from __future__ import annotations

from typing import Any

import httpx


async def process_with_llm(
    text: str,
    *,
    model: str,
    api_key: str,
    referer: str,
    context: dict[str, Any] | None = None,
) -> str:
    """Send a user message to an LLM provider and return text response."""
    payload_context = context or {}
    prompt = (
        "You are a concise assistant for real-estate leads.\n"
        f"Context: {payload_context}\n\n"
        f"User message: {text}"
    )

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            url="https://openrouter.io/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": referer,
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
