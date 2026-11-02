"""Admin authorization — allowlist by Telegram user ID only (never username,
since usernames can change / be reused). See THREAT_MODEL.md #6."""

from __future__ import annotations

from app.bot.config import settings


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids
