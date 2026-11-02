"""Telegram command handlers. Business logic stays in app/core — handlers
only validate input, enforce rate limits, dispatch to the isolated worker,
and format the reply. Errors shown to users are always generic; details go
to the log only (THREAT_MODEL.md #9)."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot import db, security
from app.bot.config import settings
from app.bot.ratelimit import get_rate_limiter
from app.bot.validation import validate_hex_input, validate_text_input
from app.worker import client as worker_client

logger = logging.getLogger("bot.handlers")
router = Router()

GENERIC_ERROR_MESSAGE = "⚠️ Xatolik yuz berdi. Keyinroq qaytadan urinib ko'ring."

HELP_TEXT = """\
🔐 <b>Cryptanalysis Bot</b>

<b>Avtomatik dekodlash:</b>
/decode &lt;matn&gt; — base64/hex/url/binary zanjirini avtomatik aniqlab ochadi

<b>Klassik shifrlarni buzish:</b>
/xor &lt;hex&gt; — takrorlanuvchi kalitli XOR (kiritish hex formatida bo'lishi kerak)
/vigenere &lt;matn&gt; — Vigenère shifrini Kasiski + IoC bilan buzadi
/substitution &lt;matn&gt; — monoalfavit o'rin almashtirishni hill-climbing bilan buzadi

Har bir so'rov uchun vaqt/CPU limiti qo'yilgan — og'ir hisoblashlar cheklangan.
"""


def _require_argument(command: CommandObject) -> str | None:
    if command.args is None or not command.args.strip():
        return None
    return command.args.strip()


async def _rate_limited(message: Message) -> bool:
    limiter = get_rate_limiter(settings.rate_limit_per_minute, settings.rate_limit_per_minute)
    if not limiter.allow(message.from_user.id):
        await message.reply("⏳ Juda ko'p so'rov. Birozdan keyin qayta urinib ko'ring.")
        return True
    return False


@router.message(Command("start"))
async def handle_start(message: Message) -> None:
    await db.get_or_create_user(message.from_user.id)
    await message.reply(
        "Salom! Men kriptotahlil botiman. Buyruqlar ro'yxati uchun /help yuboring."
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.reply(HELP_TEXT)


@router.message(Command("decode"))
async def handle_decode(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await message.reply("Foydalanish: /decode <matn>")
        return

    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await message.reply(f"❌ {validation.reason}")
        return

    outcome = await worker_client.run_job(
        "chain", text, timeout_seconds=settings.job_timeout_seconds
    )
    await db.record_job(message.from_user.id, "chain", "ok" if outcome.ok else "error")

    if not outcome.ok:
        logger.warning("decode job failed for user %s: %s", message.from_user.id, outcome.error)
        await message.reply(GENERIC_ERROR_MESSAGE)
        return

    result = outcome.result
    chain_desc = " → ".join(step["encoding"] for step in result["steps"]) or "(o'zgarishsiz)"
    status = "✅ aniqlandi" if result["is_plaintext"] else "⚠️ to'liq ochilmadi"
    await message.reply(
        f"<b>Zanjir:</b> {chain_desc}\n<b>Holat:</b> {status}\n\n<code>{result['final_text']}</code>"
    )


@router.message(Command("xor"))
async def handle_xor(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    hex_text = _require_argument(command)
    if hex_text is None:
        await message.reply("Foydalanish: /xor <hex_shifrmatn>")
        return

    validation = validate_hex_input(hex_text)
    if not validation.ok:
        await message.reply(f"❌ {validation.reason}")
        return

    outcome = await worker_client.run_job(
        "xor", hex_text, timeout_seconds=settings.job_timeout_seconds
    )
    await db.record_job(message.from_user.id, "xor", "ok" if outcome.ok else "error")

    if not outcome.ok:
        logger.warning("xor job failed for user %s: %s", message.from_user.id, outcome.error)
        await message.reply(GENERIC_ERROR_MESSAGE)
        return

    best = outcome.result["candidates"][0] if outcome.result["candidates"] else None
    if best is None:
        await message.reply("Kalit topilmadi.")
        return
    await message.reply(
        f"<b>Kalit (ascii):</b> <code>{best['key_ascii']}</code>\n"
        f"<b>Kalit uzunligi:</b> {best['key_length']}\n\n"
        f"<code>{best['plaintext']}</code>"
    )


@router.message(Command("vigenere"))
async def handle_vigenere(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await message.reply("Foydalanish: /vigenere <shifrmatn>")
        return

    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await message.reply(f"❌ {validation.reason}")
        return

    outcome = await worker_client.run_job(
        "vigenere", text, timeout_seconds=settings.job_timeout_seconds
    )
    await db.record_job(message.from_user.id, "vigenere", "ok" if outcome.ok else "error")

    if not outcome.ok:
        logger.warning("vigenere job failed for user %s: %s", message.from_user.id, outcome.error)
        await message.reply(GENERIC_ERROR_MESSAGE)
        return

    best = outcome.result["candidates"][0] if outcome.result["candidates"] else None
    if best is None:
        await message.reply("Kalit topilmadi.")
        return
    await message.reply(
        f"<b>Kalit:</b> <code>{best['key']}</code>\n\n<code>{best['plaintext']}</code>"
    )


@router.message(Command("substitution"))
async def handle_substitution(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await message.reply("Foydalanish: /substitution <shifrmatn>")
        return

    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await message.reply(f"❌ {validation.reason}")
        return

    outcome = await worker_client.run_job(
        "substitution", text, timeout_seconds=settings.job_timeout_seconds
    )
    await db.record_job(message.from_user.id, "substitution", "ok" if outcome.ok else "error")

    if not outcome.ok:
        logger.warning(
            "substitution job failed for user %s: %s", message.from_user.id, outcome.error
        )
        await message.reply(GENERIC_ERROR_MESSAGE)
        return

    await message.reply(f"<code>{outcome.result['plaintext']}</code>")


@router.message(Command("stats"))
async def handle_stats(message: Message) -> None:
    if not security.is_admin(message.from_user.id):
        await message.reply("Bu buyruq faqat adminlar uchun.")
        return
    pruned = await db.prune_expired_jobs()
    await db.add_audit_log_entry(message.from_user.id, "stats_viewed")
    await message.reply(f"📊 Tozalangan eski job yozuvlari: {pruned}")


@router.message(Command("auditlog"))
async def handle_auditlog(message: Message) -> None:
    if not security.is_admin(message.from_user.id):
        await message.reply("Bu buyruq faqat adminlar uchun.")
        return
    intact = await db.verify_audit_log_integrity()
    await db.add_audit_log_entry(message.from_user.id, "auditlog_verified")
    await message.reply("✅ Audit log yaxlit." if intact else "🚨 Audit log buzilgan!")
