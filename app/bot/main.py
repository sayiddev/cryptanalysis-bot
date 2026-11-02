"""Bot entry point — webhook mode only (no polling, per baseline item 9).

aiogram's SimpleRequestHandler verifies the X-Telegram-Bot-Api-Secret-Token
header against WEBHOOK_SECRET_TOKEN on every incoming update automatically.
"""

from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.bot import db, handlers
from app.bot.config import settings

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("bot.main")

bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(handlers.router)


async def on_startup(bot: Bot) -> None:
    await db.init_db()
    webhook_url = settings.webhook_base_url.rstrip("/") + settings.webhook_path
    await bot.set_webhook(url=webhook_url, secret_token=settings.webhook_secret_token)
    logger.info("webhook set to %s", webhook_url)


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()


def build_app() -> web.Application:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=settings.webhook_secret_token
    ).register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)
    return app


def main() -> None:
    # Binding all interfaces is required so the nginx container can reach
    # this one over the internal docker network; nginx is the only service
    # with a published port (443) in docker-compose.yml.
    web.run_app(build_app(), host="0.0.0.0", port=8080)  # nosec B104


if __name__ == "__main__":
    main()
