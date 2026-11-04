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

_COMMAND_SPECS = [
    ("start", {"uz": "Botni ishga tushirish", "ru": "Запустить бота", "en": "Start the bot"}),
    ("help", {"uz": "Yordam va buyruqlar ro'yxati", "ru": "Помощь и список команд", "en": "Help and command list"}),
    ("language", {"uz": "Tilni o'zgartirish", "ru": "Сменить язык", "en": "Change language"}),
    ("decode", {"uz": "Kodlashni avtomatik aniqlab ochish", "ru": "Автоопределение и раскрытие кодирования", "en": "Auto-detect and unwrap encoding"}),
    ("xor", {"uz": "Takrorlanuvchi kalitli XOR'ni buzish", "ru": "Взлом XOR с повторяющимся ключом", "en": "Break repeating-key XOR"}),
    ("vigenere", {"uz": "Vigenère shifrini buzish", "ru": "Взлом шифра Vigenère", "en": "Break the Vigenère cipher"}),
    ("substitution", {"uz": "Harf almashtirishni buzish", "ru": "Взлом моноалфавитной замены", "en": "Break substitution cipher"}),
    ("caesar", {"uz": "Caesar shifri bilan shifrlash", "ru": "Шифрование шифром Caesar", "en": "Encrypt with the Caesar cipher"}),
    ("vigenere_encrypt", {"uz": "Vigenère bilan shifrlash", "ru": "Шифрование Vigenère", "en": "Encrypt with Vigenère"}),
    ("xor_encrypt", {"uz": "XOR bilan shifrlash", "ru": "Шифрование XOR", "en": "Encrypt with XOR"}),
    ("substitution_encrypt", {"uz": "Tasodifiy substitution bilan shifrlash", "ru": "Шифрование случайной заменой", "en": "Encrypt with random substitution"}),
    ("sha256", {"uz": "SHA-256 hash hisoblash", "ru": "Вычислить SHA-256", "en": "Compute SHA-256 hash"}),
    ("sha1", {"uz": "SHA-1 hash hisoblash", "ru": "Вычислить SHA-1", "en": "Compute SHA-1 hash"}),
    ("md5", {"uz": "MD5 hash hisoblash", "ru": "Вычислить MD5", "en": "Compute MD5 hash"}),
    ("base64_encode", {"uz": "Base64 formatiga kodlash", "ru": "Кодировать в Base64", "en": "Encode to Base64"}),
    ("wordlists", {"uz": "Top 5 parol wordlist'ini yuklab olish", "ru": "Скачать топ-5 wordlist паролей", "en": "Download the top 5 password wordlists"}),
    ("personal_wordlist", {"uz": "Shaxsiy ma'lumotlardan wordlist yasash", "ru": "Создать wordlist из личных данных", "en": "Build a wordlist from personal info"}),
    ("genpass", {"uz": "Kuchli tasodifiy parol yasash", "ru": "Сгенерировать надёжный пароль", "en": "Generate a strong password"}),
    ("rot13", {"uz": "ROT13 shifrlash/ochish", "ru": "Шифрование/расшифровка ROT13", "en": "ROT13 encrypt/decrypt"}),
    ("rot47", {"uz": "ROT47 shifrlash/ochish", "ru": "Шифрование/расшифровка ROT47", "en": "ROT47 encrypt/decrypt"}),
    ("affine", {"uz": "Affine shifrini buzish", "ru": "Взлом шифра Affine", "en": "Break the Affine cipher"}),
    ("affine_encrypt", {"uz": "Affine bilan shifrlash", "ru": "Шифрование Affine", "en": "Encrypt with Affine"}),
    ("analyze", {"uz": "Matnning statistik tahlili (IoC, entropiya)", "ru": "Статистический анализ текста (IoC, энтропия)", "en": "Statistical text analysis (IoC, entropy)"}),
    ("history", {"uz": "So'nggi so'rovlaringiz tarixi", "ru": "История последних запросов", "en": "Your recent request history"}),
    ("randkey", {"uz": "Tasodifiy kriptografik kalit yasash", "ru": "Сгенерировать случайный ключ", "en": "Generate a random crypto key"}),
]

BOT_COMMANDS = [BotCommand(command=cmd, description=desc["uz"]) for cmd, desc in _COMMAND_SPECS]
BOT_COMMANDS_BY_LANG = {
    lang: [BotCommand(command=cmd, description=desc[lang]) for cmd, desc in _COMMAND_SPECS]
    for lang in ("ru", "en")
}

BOT_SHORT_DESCRIPTION_BY_LANG = {
    "uz": (
        "🔒 Cryptography & Cryptanalysis Toolkit — shifrlarni kalitsiz buzadi, "
        "shifrlaydi, hash hisoblaydi"
    ),
    "ru": (
        "🔒 Cryptography & Cryptanalysis Toolkit — взламывает шифры без ключа, "
        "шифрует, считает hash"
    ),
    "en": (
        "🔒 Cryptography & Cryptanalysis Toolkit — breaks ciphers without the "
        "key, encrypts, computes hashes"
    ),
}

BOT_DESCRIPTION_BY_LANG = {
    "uz": (
        "🔒 DecodeWizard — kriptotahlil boti.\n\n"
        "🔓 Noma'lum kalit bilan shifrlangan matnni buzadi: XOR, Vigenère, "
        "monoalfavit almashtirish, Affine (o'z algoritmlari, tashqi kutubxonasiz).\n"
        "🔒 Matningizni klassik shifrlar bilan shifrlaydi.\n"
        "🔍 Base64/Hex/URL kabi kodlashlarni avtomatik aniqlab ochadi.\n"
        "📊 Entropiya, Index of Coincidence kabi statistik tahlil beradi.\n"
        "🔑 Kuchli parol va wordlist generatori.\n\n"
        "Boshlash uchun pastdagi START tugmasini bosing."
    ),
    "ru": (
        "🔒 DecodeWizard — бот для криптоанализа.\n\n"
        "🔓 Взламывает зашифрованный текст без ключа: XOR, Vigenère, "
        "моноалфавитная замена, Affine (собственные алгоритмы, без сторонних "
        "библиотек).\n"
        "🔒 Шифрует ваш текст классическими шифрами.\n"
        "🔍 Автоматически определяет и раскрывает Base64/Hex/URL.\n"
        "📊 Даёт статистику — энтропию, индекс совпадений.\n"
        "🔑 Генератор надёжных паролей и wordlist.\n\n"
        "Нажмите START ниже, чтобы начать."
    ),
    "en": (
        "🔒 DecodeWizard — a cryptanalysis bot.\n\n"
        "🔓 Breaks encrypted text without the key: XOR, Vigenère, "
        "monoalphabetic substitution, Affine (own algorithms, no external "
        "libraries).\n"
        "🔒 Encrypts your text with classical ciphers.\n"
        "🔍 Auto-detects and unwraps Base64/Hex/URL encoding.\n"
        "📊 Gives statistics — entropy, Index of Coincidence.\n"
        "🔑 Strong password and wordlist generator.\n\n"
        "Tap START below to begin."
    ),
}

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
    await bot.set_my_description(description=BOT_DESCRIPTION_BY_LANG["uz"])
    await bot.set_my_short_description(short_description=BOT_SHORT_DESCRIPTION_BY_LANG["uz"])
    for lang, commands in BOT_COMMANDS_BY_LANG.items():
        await bot.set_my_commands(commands, language_code=lang)
        await bot.set_my_description(description=BOT_DESCRIPTION_BY_LANG[lang], language_code=lang)
        await bot.set_my_short_description(
            short_description=BOT_SHORT_DESCRIPTION_BY_LANG[lang], language_code=lang
        )
    webhook_url = settings.webhook_base_url.rstrip("/") + settings.webhook_path
    await bot.set_webhook(url=webhook_url, secret_token=settings.webhook_secret_token)
    logger.info("webhook set to %s", webhook_url)
    _cleanup_task = asyncio.create_task(_periodic_cleanup())


async def on_shutdown(bot: Bot) -> None:
    # Deliberately NOT calling bot.delete_webhook() here: if a second
    # instance is ever started by mistake while the first is still running,
    # its on_startup fails to bind the port and aiohttp still runs this
    # shutdown hook as cleanup — deleting the webhook would then silently
    # break the still-running first instance. set_webhook() on the next
    # real startup is idempotent, so there's nothing to clean up here.
    if _cleanup_task is not None:
        _cleanup_task.cancel()


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


def _port_in_use(port: int) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0


def main() -> None:
    port = 8080
    if _port_in_use(port):
        logger.error(
            "Port %d is already in use — another bot instance is probably still "
            "running. Stop it first (don't start a second one), then try again.",
            port,
        )
        raise SystemExit(1)

    # Binding all interfaces is required so the nginx container can reach
    # this one over the internal docker network; nginx is the only service
    # with a published port (443) in docker-compose.yml.
    web.run_app(build_app(), host="0.0.0.0", port=port)  # nosec B104


if __name__ == "__main__":
    main()
