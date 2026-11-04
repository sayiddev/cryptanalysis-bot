"""Telegram command handlers. Business logic stays in app/core — handlers
only validate input, enforce rate limits, dispatch to the isolated worker,
and format the reply. Errors shown to users are always generic; details go
to the log only (THREAT_MODEL.md #9).

Two ways to trigger an action:
  1. Type a slash command with arguments, e.g. "/decode <text>".
  2. Tap an inline button, then send the text as a plain message — this
     flow is driven by the AwaitingInput FSM state (see states.py).
Both paths converge on the same `_process_*` functions below.

Every handler resolves the caller's `lang` (from the DB, default "uz")
and threads it through formatting.* / keyboards.* so the same flow renders
in uz/ru/en — see app/bot/i18n.py for the translation tables.
"""

from __future__ import annotations

import base64
import json
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    URLInputFile,
    WebAppInfo,
)

from app.bot import db, formatting, security
from app.bot.config import settings
from app.bot.i18n import SUPPORTED_LANGUAGES, label
from app.bot.keyboards import (
    back_to_menu_keyboard,
    cancel_keyboard,
    decode_break_menu_keyboard,
    encrypt_menu_keyboard,
    hash_menu_keyboard,
    keygen_menu_keyboard,
    language_picker_keyboard,
    main_menu_keyboard,
    password_result_keyboard,
    randkey_result_keyboard,
    wordlists_menu_keyboard,
)
from app.bot.ratelimit import get_rate_limiter
from app.bot.states import AwaitingInput, PersonalWordlistForm
from app.bot.validation import validate_hex_input, validate_text_input
from app.core import (
    affine_breaker,
    classical_ciphers,
    hash_tools,
    password_gen,
    rot_ciphers,
    text_analysis,
    wordlist_gen,
)
from app.worker import client as worker_client

logger = logging.getLogger("bot.handlers")
router = Router()


async def _lang_for(user_id: int) -> str:
    return await db.get_user_language(user_id)


def _require_argument(command: CommandObject) -> str | None:
    if command.args is None or not command.args.strip():
        return None
    return command.args.strip()


def _split_first_token(args: str) -> tuple[str, str] | None:
    parts = args.split(maxsplit=1)
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


async def _rate_limited(message: Message, lang: str) -> bool:
    limiter = get_rate_limiter(settings.rate_limit_per_minute, settings.rate_limit_per_minute)
    if not limiter.allow(message.from_user.id):
        await message.reply(formatting.rate_limited(lang))
        return True
    return False


async def _reply_missing_argument(message: Message, lang: str, command_name: str) -> None:
    await message.reply(
        formatting.detail_text(lang, command_name), reply_markup=back_to_menu_keyboard(lang)
    )


async def _reply_validation_error(message: Message, lang: str, command_name: str, reason: str) -> None:
    await message.reply(f"❌ {reason}", reply_markup=back_to_menu_keyboard(lang))
    logger.info("validation failed for /%s: %s", command_name, reason)


# ── Core processing, shared by the command path and the FSM button path ──


MAX_WEBAPP_DATA_LENGTH = 1500


def _decode_webapp_keyboard(lang: str, result: dict) -> InlineKeyboardMarkup:
    payload = json.dumps(
        {
            "steps": result["steps"],
            "is_plaintext": result["is_plaintext"],
            "final_text": result["final_text"],
        }
    )
    encoded = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")

    buttons = [[InlineKeyboardButton(text=label(lang, "menu"), callback_data="menu:main")]]
    if len(encoded) <= MAX_WEBAPP_DATA_LENGTH:
        url = f"{settings.webhook_base_url.rstrip('/')}/webapp/decode?data={encoded}"
        buttons.insert(
            0, [InlineKeyboardButton(text=label(lang, "visual_view"), web_app=WebAppInfo(url=url))]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def _process_decode(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "decode", validation.reason)
        return

    outcome = await worker_client.run_job(
        "chain", text, timeout_seconds=settings.job_timeout_seconds
    )
    await db.record_job(message.from_user.id, "chain", "ok" if outcome.ok else "error")

    if not outcome.ok:
        logger.warning("decode job failed for user %s: %s", message.from_user.id, outcome.error)
        await message.reply(formatting.generic_error(lang))
        return

    result = outcome.result
    chain_desc = " → ".join(step["encoding"] for step in result["steps"]) or "(—)"
    await message.reply(
        formatting.decode_result(lang, chain_desc, result["is_plaintext"], result["final_text"]),
        reply_markup=_decode_webapp_keyboard(lang, result),
    )


async def _process_xor(message: Message, lang: str, hex_text: str) -> None:
    validation = validate_hex_input(hex_text)
    if not validation.ok:
        await _reply_validation_error(message, lang, "xor", validation.reason)
        return

    outcome = await worker_client.run_job(
        "xor", hex_text, timeout_seconds=settings.job_timeout_seconds
    )
    await db.record_job(message.from_user.id, "xor", "ok" if outcome.ok else "error")

    if not outcome.ok:
        logger.warning("xor job failed for user %s: %s", message.from_user.id, outcome.error)
        await message.reply(formatting.generic_error(lang))
        return

    best = outcome.result["candidates"][0] if outcome.result["candidates"] else None
    if best is None:
        await message.reply(label(lang, "key_not_found"), reply_markup=back_to_menu_keyboard(lang))
        return
    await message.reply(
        formatting.xor_result(lang, best["key_ascii"], best["key_length"], best["plaintext"]),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_vigenere(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "vigenere", validation.reason)
        return

    outcome = await worker_client.run_job(
        "vigenere", text, timeout_seconds=settings.job_timeout_seconds
    )
    await db.record_job(message.from_user.id, "vigenere", "ok" if outcome.ok else "error")

    if not outcome.ok:
        logger.warning("vigenere job failed for user %s: %s", message.from_user.id, outcome.error)
        await message.reply(formatting.generic_error(lang))
        return

    best = outcome.result["candidates"][0] if outcome.result["candidates"] else None
    if best is None:
        await message.reply(label(lang, "key_not_found"), reply_markup=back_to_menu_keyboard(lang))
        return
    await message.reply(
        formatting.vigenere_result(lang, best["key"], best["plaintext"]),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_substitution(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "substitution", validation.reason)
        return

    outcome = await worker_client.run_job(
        "substitution", text, timeout_seconds=settings.job_timeout_seconds
    )
    await db.record_job(message.from_user.id, "substitution", "ok" if outcome.ok else "error")

    if not outcome.ok:
        logger.warning(
            "substitution job failed for user %s: %s", message.from_user.id, outcome.error
        )
        await message.reply(formatting.generic_error(lang))
        return

    await message.reply(
        formatting.substitution_result(lang, outcome.result["plaintext"]),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_caesar(message: Message, lang: str, args: str) -> None:
    split = _split_first_token(args)
    if split is None:
        await _reply_missing_argument(message, lang, "caesar")
        return
    shift_str, text = split
    try:
        shift = int(shift_str)
    except ValueError:
        await _reply_validation_error(message, lang, "caesar", label(lang, "shift_must_be_integer"))
        return
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "caesar", validation.reason)
        return
    ciphertext = classical_ciphers.caesar_encrypt(text, shift)
    await message.reply(
        formatting.caesar_encrypted(lang, shift, ciphertext),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_vigenere_encrypt(message: Message, lang: str, args: str) -> None:
    split = _split_first_token(args)
    if split is None:
        await _reply_missing_argument(message, lang, "vigenere_encrypt")
        return
    key, text = split
    if not key.isalpha():
        await _reply_validation_error(
            message, lang, "vigenere_encrypt", label(lang, "key_letters_only")
        )
        return
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "vigenere_encrypt", validation.reason)
        return
    ciphertext = classical_ciphers.vigenere_encrypt(text, key)
    await message.reply(
        formatting.vigenere_encrypted(lang, key, ciphertext),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_xor_encrypt(message: Message, lang: str, args: str) -> None:
    split = _split_first_token(args)
    if split is None:
        await _reply_missing_argument(message, lang, "xor_encrypt")
        return
    key, text = split
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "xor_encrypt", validation.reason)
        return
    ciphertext_hex = classical_ciphers.xor_encrypt_hex(text, key)
    await message.reply(
        formatting.xor_encrypted(lang, key, ciphertext_hex),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_substitution_encrypt(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "substitution_encrypt", validation.reason)
        return
    ciphertext, _mapping = classical_ciphers.random_substitution_encrypt(text)
    await message.reply(
        formatting.substitution_encrypted(lang, ciphertext),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_sha256(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "sha256", validation.reason)
        return
    await message.reply(
        formatting.hash_result(lang, "SHA-256", hash_tools.sha256_hex(text)),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_sha1(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "sha1", validation.reason)
        return
    await message.reply(
        formatting.hash_result(lang, "SHA-1", hash_tools.sha1_hex(text)),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_md5(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "md5", validation.reason)
        return
    await message.reply(
        formatting.hash_result(lang, "MD5", hash_tools.md5_hex(text)),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_base64_encode(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "base64_encode", validation.reason)
        return
    await message.reply(
        formatting.base64_encoded(lang, hash_tools.base64_encode(text)),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _generate_and_send_wordlist(
    message: Message, lang: str, words: list[str], years: list[str]
) -> None:
    candidates = wordlist_gen.generate_personal_wordlist(words, years)
    content = "\n".join(candidates).encode("utf-8")

    # THREAT_MODEL.md: never persist the personal input itself, only that
    # this action happened (data minimization + audit trail).
    await db.record_job(message.from_user.id, "personal_wordlist", "ok")

    await message.reply_document(
        BufferedInputFile(content, filename="wordlist.txt"),
        caption=f"🎯 {len(candidates)} {label(lang, 'words_generated')}",
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_personal_wordlist(message: Message, lang: str, text: str) -> None:
    """Quick one-line form: /personal_wordlist John, Smith, 1995"""
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "personal_wordlist", validation.reason)
        return

    tokens = [t.strip() for t in text.split(",") if t.strip()]
    years = [t for t in tokens if t.isdigit() and len(t) == 4]
    words = [t for t in tokens if t not in years]

    if not words:
        await _reply_validation_error(
            message, lang, "personal_wordlist", label(lang, "need_at_least_one_name")
        )
        return

    await _generate_and_send_wordlist(message, lang, words, years)


async def _process_rot13(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "rot13", validation.reason)
        return
    await message.reply(
        formatting.rot_result(lang, "ROT13", rot_ciphers.rot13(text)),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_rot47(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "rot47", validation.reason)
        return
    await message.reply(
        formatting.rot_result(lang, "ROT47", rot_ciphers.rot47(text)),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_affine(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "affine", validation.reason)
        return
    results = affine_breaker.crack_affine(text, candidates=1)
    if not results:
        await message.reply(label(lang, "key_not_found"), reply_markup=back_to_menu_keyboard(lang))
        return
    best = results[0]
    await message.reply(
        formatting.affine_result(lang, best.a, best.b, best.plaintext),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_affine_encrypt(message: Message, lang: str, args: str) -> None:
    parts = args.split(maxsplit=2)
    if len(parts) != 3:
        await _reply_missing_argument(message, lang, "affine_encrypt")
        return
    a_str, b_str, text = parts
    if not (a_str.lstrip("-").isdigit() and b_str.lstrip("-").isdigit()):
        await _reply_validation_error(
            message, lang, "affine_encrypt", label(lang, "ab_must_be_integers")
        )
        return
    a, b = int(a_str), int(b_str)
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "affine_encrypt", validation.reason)
        return
    try:
        ciphertext = affine_breaker.affine_encrypt(text, a, b)
    except ValueError as exc:
        await _reply_validation_error(message, lang, "affine_encrypt", str(exc))
        return
    await message.reply(
        formatting.affine_encrypted(lang, a, b, ciphertext),
        reply_markup=back_to_menu_keyboard(lang),
    )


async def _process_analyze(message: Message, lang: str, text: str) -> None:
    validation = validate_text_input(text, settings.max_input_bytes)
    if not validation.ok:
        await _reply_validation_error(message, lang, "analyze", validation.reason)
        return
    analysis = text_analysis.analyze_text(text)
    await message.reply(
        formatting.analysis_result(lang, analysis), reply_markup=back_to_menu_keyboard(lang)
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
    "rot13": _process_rot13,
    "rot47": _process_rot47,
    "affine": _process_affine,
    "affine_encrypt": _process_affine_encrypt,
    "analyze": _process_analyze,
}


# ── Commands ──


@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    is_new = await db.get_or_create_user(message.from_user.id)
    if is_new:
        await message.reply(
            formatting.language_picker_text("uz"), reply_markup=language_picker_keyboard()
        )
        return
    lang = await _lang_for(message.from_user.id)
    await message.reply(formatting.welcome_text(lang), reply_markup=main_menu_keyboard(lang))


@router.message(Command("language"))
async def handle_language_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(message.from_user.id)
    await message.reply(formatting.language_picker_text(lang), reply_markup=language_picker_keyboard())


@router.message(Command("help"))
async def handle_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(message.from_user.id)
    await message.reply(formatting.help_text(lang), reply_markup=main_menu_keyboard(lang))


@router.message(Command("decode"))
async def handle_decode(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "decode")
        return
    await _process_decode(message, lang, text)


@router.message(Command("xor"))
async def handle_xor(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "xor")
        return
    await _process_xor(message, lang, text)


@router.message(Command("vigenere"))
async def handle_vigenere(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "vigenere")
        return
    await _process_vigenere(message, lang, text)


@router.message(Command("substitution"))
async def handle_substitution(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "substitution")
        return
    await _process_substitution(message, lang, text)


@router.message(Command("caesar"))
async def handle_caesar(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    args = _require_argument(command)
    if args is None:
        await _reply_missing_argument(message, lang, "caesar")
        return
    await _process_caesar(message, lang, args)


@router.message(Command("vigenere_encrypt"))
async def handle_vigenere_encrypt(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    args = _require_argument(command)
    if args is None:
        await _reply_missing_argument(message, lang, "vigenere_encrypt")
        return
    await _process_vigenere_encrypt(message, lang, args)


@router.message(Command("xor_encrypt"))
async def handle_xor_encrypt(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    args = _require_argument(command)
    if args is None:
        await _reply_missing_argument(message, lang, "xor_encrypt")
        return
    await _process_xor_encrypt(message, lang, args)


@router.message(Command("substitution_encrypt"))
async def handle_substitution_encrypt(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "substitution_encrypt")
        return
    await _process_substitution_encrypt(message, lang, text)


@router.message(Command("sha256"))
async def handle_sha256(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "sha256")
        return
    await _process_sha256(message, lang, text)


@router.message(Command("sha1"))
async def handle_sha1(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "sha1")
        return
    await _process_sha1(message, lang, text)


@router.message(Command("md5"))
async def handle_md5(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "md5")
        return
    await _process_md5(message, lang, text)


@router.message(Command("base64_encode"))
async def handle_base64_encode(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "base64_encode")
        return
    await _process_base64_encode(message, lang, text)


@router.message(Command("rot13"))
async def handle_rot13(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "rot13")
        return
    await _process_rot13(message, lang, text)


@router.message(Command("rot47"))
async def handle_rot47(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "rot47")
        return
    await _process_rot47(message, lang, text)


@router.message(Command("affine"))
async def handle_affine(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "affine")
        return
    await _process_affine(message, lang, text)


@router.message(Command("affine_encrypt"))
async def handle_affine_encrypt(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    args = _require_argument(command)
    if args is None:
        await _reply_missing_argument(message, lang, "affine_encrypt")
        return
    await _process_affine_encrypt(message, lang, args)


@router.message(Command("analyze"))
async def handle_analyze(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "analyze")
        return
    await _process_analyze(message, lang, text)


@router.message(Command("history"))
async def handle_history(message: Message) -> None:
    lang = await _lang_for(message.from_user.id)
    jobs = await db.get_recent_jobs(message.from_user.id, limit=10)
    await message.reply(
        formatting.history_result(lang, jobs), reply_markup=back_to_menu_keyboard(lang)
    )


@router.message(Command("randkey"))
async def handle_randkey(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    args = (command.args or "").strip().lower().split()
    kind = args[0] if args and args[0] in ("alpha", "hex") else "alpha"
    length = int(args[1]) if len(args) > 1 and args[1].isdigit() else 8

    key = (
        password_gen.generate_random_hex_key(length)
        if kind == "hex"
        else password_gen.generate_random_alpha_key(length)
    )

    await message.reply(
        formatting.random_key_generated(lang, key),
        reply_markup=randkey_result_keyboard(lang, kind, length),
    )


@router.message(Command("wordlists"))
async def handle_wordlists_command(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(message.from_user.id)
    await message.reply(
        formatting.wordlists_text(lang),
        reply_markup=wordlists_menu_keyboard(lang, formatting.WORDLIST_FILES),
    )


@router.message(Command("personal_wordlist"))
async def handle_personal_wordlist_command(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    text = _require_argument(command)
    if text is None:
        await _reply_missing_argument(message, lang, "personal_wordlist")
        return
    await _process_personal_wordlist(message, lang, text)


@router.message(Command("genpass"))
async def handle_genpass_command(message: Message, command: CommandObject) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    length = password_gen.DEFAULT_LENGTH
    if command.args and command.args.strip().isdigit():
        length = int(command.args.strip())
    password = password_gen.generate_strong_password(length)
    await message.reply(
        formatting.password_generated(lang, password),
        reply_markup=password_result_keyboard(lang, length),
    )


@router.message(Command("stats"))
async def handle_stats(message: Message) -> None:
    lang = await _lang_for(message.from_user.id)
    if not security.is_admin(message.from_user.id):
        await message.reply(formatting.admin_only(lang))
        return
    pruned = await db.prune_expired_jobs()
    await db.add_audit_log_entry(message.from_user.id, "stats_viewed")
    await message.reply(f"{label(lang, 'pruned_jobs')} {pruned}")


@router.message(Command("auditlog"))
async def handle_auditlog(message: Message) -> None:
    lang = await _lang_for(message.from_user.id)
    if not security.is_admin(message.from_user.id):
        await message.reply(formatting.admin_only(lang))
        return
    intact = await db.verify_audit_log_integrity()
    await db.add_audit_log_entry(message.from_user.id, "auditlog_verified")
    await message.reply(
        label(lang, "audit_log_intact") if intact else label(lang, "audit_log_broken")
    )


# ── Inline menu navigation ──


async def _safe_edit(callback: CallbackQuery, text: str, reply_markup) -> None:
    """edit_text fails on non-text messages (e.g. a document reply) — Telegram
    simply refuses the API call. Fall back to sending a new message instead
    of leaving the button looking unresponsive."""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=reply_markup)


@router.callback_query(F.data == "menu:main")
async def handle_menu_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(callback.from_user.id)
    await _safe_edit(callback, formatting.welcome_text(lang), main_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:encrypt")
async def handle_menu_encrypt(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(callback.from_user.id)
    await _safe_edit(callback, formatting.detail_text(lang, "encrypt"), encrypt_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:help")
async def handle_menu_help(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(callback.from_user.id)
    await _safe_edit(callback, formatting.help_text(lang), main_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:language")
async def handle_menu_language(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(callback.from_user.id)
    await _safe_edit(callback, formatting.language_picker_text(lang), language_picker_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("setlang:"))
async def handle_set_language(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    new_lang = callback.data.split(":", 1)[1]
    if new_lang not in SUPPORTED_LANGUAGES:
        await callback.answer()
        return
    await db.set_user_language(callback.from_user.id, new_lang)
    await _safe_edit(callback, formatting.welcome_text(new_lang), main_menu_keyboard(new_lang))
    await callback.answer(formatting.language_set_confirm(new_lang))


@router.callback_query(F.data == "menu:wordlists")
async def handle_menu_wordlists(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(callback.from_user.id)
    await _safe_edit(
        callback,
        formatting.wordlists_text(lang),
        wordlists_menu_keyboard(lang, formatting.WORDLIST_FILES),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:decode_break")
async def handle_menu_decode_break(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(callback.from_user.id)
    await _safe_edit(
        callback, formatting.decode_break_menu_text(lang), decode_break_menu_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:hash")
async def handle_menu_hash(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(callback.from_user.id)
    await _safe_edit(callback, formatting.hash_menu_text(lang), hash_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:keygen")
async def handle_menu_keygen(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(callback.from_user.id)
    await _safe_edit(callback, formatting.keygen_menu_text(lang), keygen_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:history")
async def handle_menu_history(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang_for(callback.from_user.id)
    jobs = await db.get_recent_jobs(callback.from_user.id, limit=10)
    await _safe_edit(callback, formatting.history_result(lang, jobs), back_to_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("randkey:"))
async def handle_randkey_button(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.from_user.id)
    if await _rate_limited(callback.message, lang):
        await callback.answer()
        return
    _, kind, length_str = callback.data.split(":")
    length = int(length_str)
    key = (
        password_gen.generate_random_hex_key(length)
        if kind == "hex"
        else password_gen.generate_random_alpha_key(length)
    )
    await callback.message.answer(
        formatting.random_key_generated(lang, key),
        reply_markup=randkey_result_keyboard(lang, kind, length),
    )
    await callback.answer()


_WORDLISTS_BY_KEY = {wl["key"]: wl for wl in formatting.WORDLIST_FILES}


@router.callback_query(F.data.startswith("getfile:"))
async def handle_get_wordlist_file(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.from_user.id)
    key = callback.data.split(":", 1)[1]
    wordlist = _WORDLISTS_BY_KEY.get(key)
    if wordlist is None:
        await callback.answer(label(lang, "not_found"))
        return
    if await _rate_limited(callback.message, lang):
        await callback.answer()
        return

    await callback.answer(f"{label(lang, 'loading')} ({wordlist['size']})")
    try:
        description = formatting.wordlist_description(lang, key)
        await callback.message.answer_document(
            URLInputFile(wordlist["url"], filename=wordlist["name"]),
            caption=(
                f"📋 {wordlist['name']}\n{description}\n\n"
                f"{label(lang, 'source_label')} SecLists (MIT license)"
            ),
        )
    except Exception:
        logger.exception("failed to send wordlist file %s", key)
        await callback.message.answer(formatting.generic_error(lang))


@router.callback_query(F.data.startswith("genpass:"))
async def handle_generate_password(callback: CallbackQuery) -> None:
    lang = await _lang_for(callback.from_user.id)
    if await _rate_limited(callback.message, lang):
        await callback.answer()
        return
    try:
        length = int(callback.data.split(":", 1)[1])
    except ValueError:
        length = password_gen.DEFAULT_LENGTH

    password = password_gen.generate_strong_password(length)
    await callback.message.answer(
        formatting.password_generated(lang, password),
        reply_markup=password_result_keyboard(lang, length),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("action:"))
async def handle_action_button(callback: CallbackQuery, state: FSMContext) -> None:
    lang = await _lang_for(callback.from_user.id)
    action = callback.data.split(":", 1)[1]
    if action == "personal_wordlist":
        await state.set_state(PersonalWordlistForm.name)
        await state.update_data(words=[], years=[])
        await _safe_edit(callback, label(lang, "wordlist_step1"), cancel_keyboard(lang))
        await callback.answer()
        return
    if action not in _ACTIONS:
        await callback.answer()
        return
    await state.set_state(AwaitingInput.waiting)
    await state.update_data(action=action)
    await _safe_edit(callback, formatting.action_prompt(lang, action), cancel_keyboard(lang))
    await callback.answer()


# ── Step-by-step personal wordlist form ──


@router.message(StateFilter(PersonalWordlistForm.name), F.text, ~F.text.startswith("/"))
async def handle_wordlist_name(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.from_user.id)
    name = message.text.strip()
    if not name:
        await message.reply(label(lang, "enter_name"), reply_markup=cancel_keyboard(lang))
        return
    data = await state.get_data()
    words = data.get("words", [])
    words.append(name)
    await state.update_data(words=words)
    await state.set_state(PersonalWordlistForm.nickname)
    await message.reply(label(lang, "wordlist_step2"), reply_markup=cancel_keyboard(lang))


@router.message(StateFilter(PersonalWordlistForm.nickname), F.text, ~F.text.startswith("/"))
async def handle_wordlist_nickname(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.from_user.id)
    text = message.text.strip()
    if text and text != "-":
        data = await state.get_data()
        words = data.get("words", [])
        words.append(text)
        await state.update_data(words=words)
    await state.set_state(PersonalWordlistForm.birth_year)
    await message.reply(label(lang, "wordlist_step3"), reply_markup=cancel_keyboard(lang))


@router.message(StateFilter(PersonalWordlistForm.birth_year), F.text, ~F.text.startswith("/"))
async def handle_wordlist_birth_year(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.from_user.id)
    text = message.text.strip()
    if text and text != "-":
        if not (text.isdigit() and len(text) == 4):
            await message.reply(
                label(lang, "wordlist_step3_error"), reply_markup=cancel_keyboard(lang)
            )
            return
        data = await state.get_data()
        years = data.get("years", [])
        years.append(text)
        await state.update_data(years=years)
    await state.set_state(PersonalWordlistForm.extra)
    await message.reply(label(lang, "wordlist_step4"), reply_markup=cancel_keyboard(lang))


@router.message(StateFilter(PersonalWordlistForm.extra), F.text, ~F.text.startswith("/"))
async def handle_wordlist_extra(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.from_user.id)
    text = message.text.strip()
    data = await state.get_data()
    words = data.get("words", [])
    years = data.get("years", [])
    if text and text != "-":
        words.append(text)
    await state.clear()

    if not words:
        await message.reply(
            label(lang, "need_at_least_one_word"), reply_markup=back_to_menu_keyboard(lang)
        )
        return
    if await _rate_limited(message, lang):
        return
    await _generate_and_send_wordlist(message, lang, words, years)


# ── Plain-text input while an action button is pending ──


@router.message(StateFilter(AwaitingInput.waiting), F.text, ~F.text.startswith("/"))
async def handle_pending_action_input(message: Message, state: FSMContext) -> None:
    lang = await _lang_for(message.from_user.id)
    if await _rate_limited(message, lang):
        return
    data = await state.get_data()
    action = data.get("action")
    await state.clear()

    handler = _ACTIONS.get(action)
    if handler is None:
        await message.reply(formatting.generic_error(lang))
        return
    await handler(message, lang, message.text.strip())


@router.message(F.text, ~F.text.startswith("/"))
async def handle_stray_text(message: Message) -> None:
    """Any plain text with no pending action and no matching command.

    Without this, such messages are silently dropped (no handler matches),
    which looks like the bot ignoring the user. Registered last so it never
    shadows a real command or an active AwaitingInput state.
    """
    lang = await _lang_for(message.from_user.id)
    await message.reply(formatting.stray_text(lang), reply_markup=main_menu_keyboard(lang))
