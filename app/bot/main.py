"""Bot entry point — webhook mode only (no polling, per baseline item 9).

aiogram's SimpleRequestHandler verifies the X-Telegram-Bot-Api-Secret-Token
header against WEBHOOK_SECRET_TOKEN on every incoming update automatically.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.bot import db, handlers
from app.bot.config import settings

BOT_COMMANDS = [
    BotCommand(command="start", description="Botni ishga tushirish"),
    BotCommand(command="help", description="Yordam va buyruqlar ro'yxati"),
    BotCommand(command="decode", description="Kodlashni avtomatik aniqlab ochish"),
    BotCommand(command="xor", description="Takrorlanuvchi kalitli XOR'ni buzish"),
    BotCommand(command="vigenere", description="Vigenère shifrini buzish"),
    BotCommand(command="substitution", description="Harf almashtirishni buzish"),
    BotCommand(command="caesar", description="Caesar shifri bilan shifrlash"),
    BotCommand(command="vigenere_encrypt", description="Vigenère bilan shifrlash"),
    BotCommand(command="xor_encrypt", description="XOR bilan shifrlash"),
    BotCommand(command="substitution_encrypt", description="Tasodifiy substitution bilan shifrlash"),
    BotCommand(command="sha256", description="SHA-256 hash hisoblash"),
    BotCommand(command="sha1", description="SHA-1 hash hisoblash"),
    BotCommand(command="md5", description="MD5 hash hisoblash"),
    BotCommand(command="base64_encode", description="Base64 formatiga kodlash"),
    BotCommand(command="wordlists", description="Top 5 parol wordlist'ini yuklab olish"),
    BotCommand(command="personal_wordlist", description="Shaxsiy ma'lumotlardan wordlist yasash"),
]

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("bot.main")

bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(handlers.router)


CLEANUP_INTERVAL_SECONDS = 6 * 60 * 60  # data minimization: THREAT_MODEL.md #12

_cleanup_task: asyncio.Task | None = None


async def _periodic_cleanup() -> None:
    while True:
        try:
            pruned = await db.prune_expired_jobs()
            if pruned:
                logger.info("cleanup: pruned %d expired job records", pruned)
        except Exception:
            logger.exception("periodic cleanup failed")
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)


async def on_startup(bot: Bot) -> None:
    global _cleanup_task
    await db.init_db()
    await bot.set_my_commands(BOT_COMMANDS)
    webhook_url = settings.webhook_base_url.rstrip("/") + settings.webhook_path
    await bot.set_webhook(url=webhook_url, secret_token=settings.webhook_secret_token)
    logger.info("webhook set to %s", webhook_url)
    _cleanup_task = asyncio.create_task(_periodic_cleanup())


async def on_shutdown(bot: Bot) -> None:
    if _cleanup_task is not None:
        _cleanup_task.cancel()
    await bot.delete_webhook()


_WEBAPP_DIR = Path(__file__).parent / "webapp"


async def _serve_decode_webapp(request: web.Request) -> web.Response:
    html = (_WEBAPP_DIR / "decode.html").read_text(encoding="utf-8")
    return web.Response(text=html, content_type="text/html")


def build_app() -> web.Application:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=settings.webhook_secret_token
    ).register(app, path=settings.webhook_path)
    app.router.add_get("/webapp/decode", _serve_decode_webapp)
    setup_application(app, dp, bot=bot)
    return app


def main() -> None:
    # Binding all interfaces is required so the nginx container can reach
    # this one over the internal docker network; nginx is the only service
    # with a published port (443) in docker-compose.yml.
    web.run_app(build_app(), host="0.0.0.0", port=8080)  # nosec B104


if __name__ == "__main__":
    main()
