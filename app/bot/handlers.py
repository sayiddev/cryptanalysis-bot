"""Telegram command handlers. Business logic stays in app/core — handlers
only validate input, enforce rate limits, dispatch to the isolated worker,
and format the reply. Errors shown to users are always generic; details go
to the log only (THREAT_MODEL.md #9)."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from app.bot import db, formatting, security
from app.bot.config import settings
from app.bot.keyboards import back_to_menu_keyboard, main_menu_keyboard
from app.bot.ratelimit import get_rate_limiter
from app.bot.validation import validate_hex_input, validate_text_input
from app.worker import client as worker_client

logger = logging.getLogger("bot.handlers")
router = Router()

GENERIC_ERROR_MESSAGE = "⚠️ Xatolik yuz berdi. Keyinroq qaytadan urinib ko'ring."


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


async def _reply_missing_argument(message: Message, command_name: str) -> None:
    await message.reply(
        formatting.detail_text(command_name), reply_markup=back_to_menu_keyboard()
    )


async def _reply_validation_error(message: Message, command_name: str, reason: str) -> None:
    await message.reply(
        f"❌ {reason}\n\n<i>Misol uchun quyidagi tugmani bosing:</i>",
        reply_markup=back_to_menu_keyboard(),
    )
    logger.info("validation failed for /%s: %s", command_name, reason)


@router.message(Command("start"))
async def handle_start(message: Message) -> None:
    await db.get_or_create_user(message.from_user.id)
    await message.reply(formatting.WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.reply(formatting.HELP_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "menu:main")
async def handle_menu_main(callback: CallbackQuery) -> None:
    await callback.message.edit_text(formatting.WELCOME_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:help")
async def handle_menu_help(callback: CallbackQuery) -> None:
    await callback.message.edit_text(formatting.HELP_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("menu:"))
async def handle_menu_detail(callback: CallbackQuery) -> None:
    command_name = callback.data.split(":", 1)[1]
    await callback.message.edit_text(
        formatting.detail_text(command_name), reply_markup=back_to_menu_keyboard()
    )
    await callback.answer()


@router.message(Command("decode"))
async def handle_decode(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "decode")
        return

    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "decode", validation.reason)
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
    await message.reply(
        formatting.decode_result(chain_desc, result["is_plaintext"], result["final_text"])
    )


@router.message(Command("xor"))
async def handle_xor(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    hex_text = _require_argument(command)
    if hex_text is None:
        await _reply_missing_argument(message, "xor")
        return

    validation = validate_hex_input(hex_text)
    if not validation.ok:
        await _reply_validation_error(message, "xor", validation.reason)
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
        await message.reply("🤷 Kalit topilmadi.")
        return
    await message.reply(
        formatting.xor_result(best["key_ascii"], best["key_length"], best["plaintext"])
    )


@router.message(Command("vigenere"))
async def handle_vigenere(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "vigenere")
        return

    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "vigenere", validation.reason)
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
        await message.reply("🤷 Kalit topilmadi.")
        return
    await message.reply(formatting.vigenere_result(best["key"], best["plaintext"]))


@router.message(Command("substitution"))
async def handle_substitution(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "substitution")
        return

    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "substitution", validation.reason)
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

    await message.reply(formatting.substitution_result(outcome.result["plaintext"]))


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
