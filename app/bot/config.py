"""All configuration comes from environment variables (.env in dev, real
env vars in the container) — never hardcoded, per the mandatory security
baseline. See .env.example for the full list."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str
    webhook_secret_token: str
    webhook_base_url: str
    webhook_path: str = "/webhook"

    admin_user_ids: str = ""  # comma-separated Telegram user IDs

    database_url: str = "sqlite+aiosqlite:///./data/bot.db"

    rate_limit_per_minute: int = 10
    max_input_bytes: int = 65536
    job_timeout_seconds: int = 20
    job_memory_limit_mb: int = 256

    log_level: str = "INFO"

    @property
    def admin_ids(self) -> set[int]:
        return {int(x) for x in self.admin_user_ids.split(",") if x.strip()}


settings = Settings()  # type: ignore[call-arg]  # populated from .env / real env vars
