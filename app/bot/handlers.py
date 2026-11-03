"""Telegram command handlers. Business logic stays in app/core — handlers
only validate input, enforce rate limits, dispatch to the isolated worker,
and format the reply. Errors shown to users are always generic; details go
to the log only (THREAT_MODEL.md #9).

Two ways to trigger an action:
  1. Type a slash command with arguments, e.g. "/decode <text>".
  2. Tap an inline button, then send the text as a plain message — this
     flow is driven by the AwaitingInput FSM state (see states.py).
Both paths converge on the same `_process_*` functions below.
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot import db, formatting, security
from app.bot.config import settings
from app.bot.keyboards import (
    back_to_menu_keyboard,
    cancel_keyboard,
    encrypt_menu_keyboard,
    main_menu_keyboard,
)
from app.bot.ratelimit import get_rate_limiter
from app.bot.states import AwaitingInput
from app.bot.validation import validate_hex_input, validate_text_input
from app.core import classical_ciphers, hash_tools
from app.worker import client as worker_client

logger = logging.getLogger("bot.handlers")
router = Router()

GENERIC_ERROR_MESSAGE = "⚠️ Xatolik yuz berdi. Keyinroq qaytadan urinib ko'ring."


def _require_argument(command: CommandObject) -> str | None:
    if command.args is None or not command.args.strip():
        return None
    return command.args.strip()


def _split_first_token(args: str) -> tuple[str, str] | None:
    parts = args.split(maxsplit=1)
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


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
    await message.reply(f"❌ {reason}", reply_markup=back_to_menu_keyboard())
    logger.info("validation failed for /%s: %s", command_name, reason)


# ── Core processing, shared by the command path and the FSM button path ──


async def _process_decode(message: Message, text: str) -> None:
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
        formatting.decode_result(chain_desc, result["is_plaintext"], result["final_text"]),
        reply_markup=back_to_menu_keyboard(),
    )


async def _process_xor(message: Message, hex_text: str) -> None:
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
        await message.reply("🤷 Kalit topilmadi.", reply_markup=back_to_menu_keyboard())
        return
    await message.reply(
        formatting.xor_result(best["key_ascii"], best["key_length"], best["plaintext"]),
        reply_markup=back_to_menu_keyboard(),
    )


async def _process_vigenere(message: Message, text: str) -> None:
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
        await message.reply("🤷 Kalit topilmadi.", reply_markup=back_to_menu_keyboard())
        return
    await message.reply(
        formatting.vigenere_result(best["key"], best["plaintext"]),
        reply_markup=back_to_menu_keyboard(),
    )


async def _process_substitution(message: Message, text: str) -> None:
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

    await message.reply(
        formatting.substitution_result(outcome.result["plaintext"]),
        reply_markup=back_to_menu_keyboard(),
    )


async def _process_caesar(message: Message, args: str) -> None:
    split = _split_first_token(args)
    if split is None:
        await _reply_missing_argument(message, "caesar")
        return
    shift_str, text = split
    try:
        shift = int(shift_str)
    except ValueError:
        await _reply_validation_error(message, "caesar", "shift butun son bo'lishi kerak")
        return
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "caesar", validation.reason)
        return
    ciphertext = classical_ciphers.caesar_encrypt(text, shift)
    await message.reply(
        formatting.caesar_encrypted(shift, ciphertext), reply_markup=back_to_menu_keyboard()
    )


async def _process_vigenere_encrypt(message: Message, args: str) -> None:
    split = _split_first_token(args)
    if split is None:
        await _reply_missing_argument(message, "vigenere_encrypt")
        return
    key, text = split
    if not key.isalpha():
        await _reply_validation_error(
            message, "vigenere_encrypt", "kalit faqat harflardan iborat bo'lishi kerak"
        )
        return
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "vigenere_encrypt", validation.reason)
        return
    ciphertext = classical_ciphers.vigenere_encrypt(text, key)
    await message.reply(
        formatting.vigenere_encrypted(key, ciphertext), reply_markup=back_to_menu_keyboard()
    )


async def _process_xor_encrypt(message: Message, args: str) -> None:
    split = _split_first_token(args)
    if split is None:
        await _reply_missing_argument(message, "xor_encrypt")
        return
    key, text = split
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "xor_encrypt", validation.reason)
        return
    ciphertext_hex = classical_ciphers.xor_encrypt_hex(text, key)
    await message.reply(
        formatting.xor_encrypted(key, ciphertext_hex), reply_markup=back_to_menu_keyboard()
    )


async def _process_substitution_encrypt(message: Message, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "substitution_encrypt", validation.reason)
        return
    ciphertext, _mapping = classical_ciphers.random_substitution_encrypt(text)
    await message.reply(
        formatting.substitution_encrypted(ciphertext), reply_markup=back_to_menu_keyboard()
    )


async def _process_sha256(message: Message, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "sha256", validation.reason)
        return
    await message.reply(
        formatting.hash_result("SHA-256", hash_tools.sha256_hex(text)),
        reply_markup=back_to_menu_keyboard(),
    )


async def _process_sha1(message: Message, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "sha1", validation.reason)
        return
    await message.reply(
        formatting.hash_result("SHA-1", hash_tools.sha1_hex(text)),
        reply_markup=back_to_menu_keyboard(),
    )


async def _process_md5(message: Message, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "md5", validation.reason)
        return
    await message.reply(
        formatting.hash_result("MD5", hash_tools.md5_hex(text)),
        reply_markup=back_to_menu_keyboard(),
    )


async def _process_base64_encode(message: Message, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, "base64_encode", validation.reason)
        return
    await message.reply(
        formatting.base64_encoded(hash_tools.base64_encode(text)),
        reply_markup=back_to_menu_keyboard(),
    )


_ACTIONS = {
    "decode": _process_decode,
    "xor": _process_xor,
    "vigenere": _process_vigenere,
    "substitution": _process_substitution,
    "caesar": _process_caesar,
    "vigenere_encrypt": _process_vigenere_encrypt,
    "xor_encrypt": _process_xor_encrypt,
    "substitution_encrypt": _process_substitution_encrypt,
    "sha256": _process_sha256,
    "sha1": _process_sha1,
    "md5": _process_md5,
    "base64_encode": _process_base64_encode,
}


# ── Commands ──


@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await db.get_or_create_user(message.from_user.id)
    await message.reply(formatting.WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def handle_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.reply(formatting.HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("decode"))
async def handle_decode(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "decode")
        return
    await _process_decode(message, text)


@router.message(Command("xor"))
async def handle_xor(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "xor")
        return
    await _process_xor(message, text)


@router.message(Command("vigenere"))
async def handle_vigenere(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "vigenere")
        return
    await _process_vigenere(message, text)


@router.message(Command("substitution"))
async def handle_substitution(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "substitution")
        return
    await _process_substitution(message, text)


@router.message(Command("caesar"))
async def handle_caesar(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    args = _require_argument(command)
    if args is None:
        await _reply_missing_argument(message, "caesar")
        return
    await _process_caesar(message, args)


@router.message(Command("vigenere_encrypt"))
async def handle_vigenere_encrypt(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    args = _require_argument(command)
    if args is None:
        await _reply_missing_argument(message, "vigenere_encrypt")
        return
    await _process_vigenere_encrypt(message, args)


@router.message(Command("xor_encrypt"))
async def handle_xor_encrypt(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    args = _require_argument(command)
    if args is None:
        await _reply_missing_argument(message, "xor_encrypt")
        return
    await _process_xor_encrypt(message, args)


@router.message(Command("substitution_encrypt"))
async def handle_substitution_encrypt(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "substitution_encrypt")
        return
    await _process_substitution_encrypt(message, text)


@router.message(Command("sha256"))
async def handle_sha256(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "sha256")
        return
    await _process_sha256(message, text)


@router.message(Command("sha1"))
async def handle_sha1(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "sha1")
        return
    await _process_sha1(message, text)


@router.message(Command("md5"))
async def handle_md5(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "md5")
        return
    await _process_md5(message, text)


@router.message(Command("base64_encode"))
async def handle_base64_encode(message: Message, command: CommandObject) -> None:
    if await _rate_limited(message):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, "base64_encode")
        return
    await _process_base64_encode(message, text)


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


# ── Inline menu navigation ──


@router.callback_query(F.data == "menu:main")
async def handle_menu_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(formatting.WELCOME_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "menu:encrypt")
async def handle_menu_encrypt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        formatting.detail_text("encrypt"), reply_markup=encrypt_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "menu:help")
async def handle_menu_help(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(formatting.HELP_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("action:"))
async def handle_action_button(callback: CallbackQuery, state: FSMContext) -> None:
    action = callback.data.split(":", 1)[1]
    if action not in _ACTIONS:
        await callback.answer()
        return
    await state.set_state(AwaitingInput.waiting)
    await state.update_data(action=action)
    await callback.message.edit_text(
        formatting.ACTION_PROMPTS[action], reply_markup=cancel_keyboard()
    )
    await callback.answer()


# ── Plain-text input while an action button is pending ──


@router.message(StateFilter(AwaitingInput.waiting), F.text, ~F.text.startswith("/"))
async def handle_pending_action_input(message: Message, state: FSMContext) -> None:
    if await _rate_limited(message):
        return
    data = await state.get_data()
    action = data.get("action")
    await state.clear()

    handler = _ACTIONS.get(action)
    if handler is None:
        await message.reply(GENERIC_ERROR_MESSAGE)
        return
    await handler(message, message.text.strip())


@router.message(F.text, ~F.text.startswith("/"))
async def handle_stray_text(message: Message) -> None:
    """Any plain text with no pending action and no matching command.

    Without this, such messages are silently dropped (no handler matches),
    which looks like the bot ignoring the user. Registered last so it never
    shadows a real command or an active AwaitingInput state.
    """
    await message.reply(
        "🤔 Qaysi amalni bajarishni bilmadim. Tugmalardan birini tanlang:",
        reply_markup=main_menu_keyboard(),
    )
