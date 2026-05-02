from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    secret_key: str = "dev-secret-change-me"
    database_url: str = f"sqlite+aiosqlite:///{(DATA_DIR / 'app.db').as_posix()}"

    worker_concurrency: int = 2
    playwright_headless: int = 1
    task_min_delay: int = 15
    task_max_delay: int = 60
    search_engine: str = "yandex"
    yandex_region: int = 213
    max_serp_pages: int = 10
    proxy_list: str = ""

    telegram_bot_token: str = ""
    telegram_bot_enabled: int = 0

    demo_mode: int = 1

    @property
    def proxies(self) -> List[str]:
        return [p.strip() for p in self.proxy_list.split(",") if p.strip()]


settings = Settings()
