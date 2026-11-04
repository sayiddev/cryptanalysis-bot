"""Message templates — kept separate from handlers.py so the "what the user
sees" layer can change without touching dispatch/validation logic.

Every function takes `lang` and routes through app.bot.i18n so the same
result structure renders correctly in uz/ru/en.
"""

from __future__ import annotations

from html import escape

from app.bot import i18n
from app.bot.i18n import label


def welcome_text(lang: str) -> str:
    return i18n.t(lang, i18n.WELCOME_TEXT)


def help_text(lang: str) -> str:
    return i18n.t(lang, i18n.HELP_TEXT)


def decode_break_menu_text(lang: str) -> str:
    return i18n.t(lang, i18n.DECODE_BREAK_MENU_TEXT)


def hash_menu_text(lang: str) -> str:
    return i18n.t(lang, i18n.HASH_MENU_TEXT)


def keygen_menu_text(lang: str) -> str:
    return i18n.t(lang, i18n.KEYGEN_MENU_TEXT)


def wordlists_text(lang: str) -> str:
    return i18n.t(lang, i18n.WORDLISTS_TEXT)


def detail_text(lang: str, command: str) -> str:
    table = i18n.DETAIL_TEXTS.get(command)
    if table is None:
        return help_text(lang)
    return i18n.t(lang, table)


def action_prompt(lang: str, action: str) -> str:
    table = i18n.ACTION_PROMPTS.get(action)
    if table is None:
        return help_text(lang)
    return i18n.t(lang, table)


def wordlist_description(lang: str, key: str) -> str:
    table = i18n.WORDLIST_DESCRIPTIONS.get(key, {})
    return i18n.t(lang, table) if table else ""


WORDLIST_FILES = [
    {
        "key": "wl_top10k",
        "label": "🥇 Top 10 000",
        "name": "10k-most-common.txt",
        "size": "73 KB",
        "url": (
            "https://raw.githubusercontent.com/danielmiessler/SecLists/"
            "master/Passwords/Common-Credentials/10k-most-common.txt"
        ),
    },
    {
        "key": "wl_ncsc100k",
        "label": "🥈 NCSC Top 100 000",
        "name": "100k-most-used-passwords-NCSC.txt",
        "size": "816 KB",
        "url": (
            "https://raw.githubusercontent.com/danielmiessler/SecLists/"
            "master/Passwords/Common-Credentials/100k-most-used-passwords-NCSC.txt"
        ),
    },
    {
        "key": "wl_pwdb1m",
        "label": "🥉 Pwdb Top 1 000 000",
        "name": "Pwdb_top-1000000.txt",
        "size": "8.3 MB",
        "url": (
            "https://raw.githubusercontent.com/danielmiessler/SecLists/"
            "master/Passwords/Common-Credentials/Pwdb_top-1000000.txt"
        ),
    },
    {
        "key": "wl_worst500",
        "label": "4️⃣ Eng yomon 500",
        "name": "500-worst-passwords.txt",
        "size": "3.4 KB",
        "url": (
            "https://raw.githubusercontent.com/danielmiessler/SecLists/"
            "master/Passwords/Common-Credentials/500-worst-passwords.txt"
        ),
    },
    {
        "key": "wl_top10m",
        "label": "5️⃣ Top 10 000 000",
        "name": "xato-net-10-million-passwords.txt",
        "size": "46 MB",
        "url": (
            "https://raw.githubusercontent.com/danielmiessler/SecLists/"
            "master/Passwords/Common-Credentials/xato-net-10-million-passwords.txt"
        ),
    },
]


def generic_error(lang: str) -> str:
    return i18n.t(lang, i18n.GENERIC_ERROR)


def rate_limited(lang: str) -> str:
    return i18n.t(lang, i18n.RATE_LIMITED)


def admin_only(lang: str) -> str:
    return i18n.t(lang, i18n.ADMIN_ONLY)


def stray_text(lang: str) -> str:
    return i18n.t(lang, i18n.STRAY_TEXT)


def language_picker_text(lang: str) -> str:
    return i18n.t(lang, i18n.LANGUAGE_PICKER_TEXT)


def language_set_confirm(lang: str) -> str:
    return i18n.t(lang, i18n.LANGUAGE_SET_CONFIRM)


def decode_result(lang: str, chain_desc: str, is_plaintext: bool, final_text: str) -> str:
    status = label(lang, "status_detected") if is_plaintext else label(lang, "status_not_decoded")
    return (
        f"📥 <b>{label(lang, 'chain')}</b> {escape(chain_desc)}\n"
        f"{status}\n"
        f"———————————\n"
        f"<code>{escape(final_text)}</code>"
    )


def xor_result(lang: str, key_ascii: str, key_length: int, plaintext: str) -> str:
    return (
        f"🔑 <b>{label(lang, 'key')}</b> <code>{escape(key_ascii)}</code> "
        f"<i>({key_length} {label(lang, 'bytes')})</i>\n"
        f"———————————\n"
        f"<code>{escape(plaintext)}</code>"
    )


def vigenere_result(lang: str, key: str, plaintext: str) -> str:
    return (
        f"📜 <b>{label(lang, 'key')}</b> <code>{escape(key)}</code>\n"
        f"———————————\n"
        f"<code>{escape(plaintext)}</code>"
    )


def substitution_result(lang: str, plaintext: str) -> str:
    return f"🔤 <b>{label(lang, 'result')}</b>\n———————————\n<code>{escape(plaintext)}</code>"


def affine_result(lang: str, a: int, b: int, plaintext: str) -> str:
    return (
        f"🔢 <b>{label(lang, 'key')}</b> a={a}, b={b}\n"
        f"———————————\n<code>{escape(plaintext)}</code>"
    )


def _encrypted_template(lang: str, emoji: str, cipher_name: str, extra: str, ciphertext: str) -> str:
    return (
        f"{emoji} <b>{cipher_name} {label(lang, 'encrypted_with')}</b> <i>({extra})</i>\n"
        f"———————————\n<code>{escape(ciphertext)}</code>"
    )


def caesar_encrypted(lang: str, shift: int, ciphertext: str) -> str:
    return _encrypted_template(lang, "✉️", "Caesar", f"shift={shift}", ciphertext)


def vigenere_encrypted(lang: str, key: str, ciphertext: str) -> str:
    body = _encrypted_template(lang, "✉️", "Vigenère", f"{label(lang, 'key')} {escape(key)}", ciphertext)
    return f"{body}\n\n👉 {label(lang, 'to_break')} <code>/vigenere {escape(ciphertext)}</code>"


def xor_encrypted(lang: str, key: str, ciphertext_hex: str) -> str:
    body = _encrypted_template(lang, "✉️", "XOR", f"{label(lang, 'key')} {escape(key)}", ciphertext_hex)
    return f"{body}\n\n👉 {label(lang, 'to_break')} <code>/xor {ciphertext_hex}</code>"


def substitution_encrypted(lang: str, ciphertext: str) -> str:
    names = {
        "uz": "Tasodifiy substitution bilan",
        "ru": "Случайной заменой",
        "en": "Random substitution",
    }
    name = names.get(lang, names["uz"])
    return (
        f"✉️ <b>{name} {label(lang, 'encrypted_with')}</b>\n"
        f"———————————\n<code>{escape(ciphertext)}</code>\n\n"
        f"👉 {label(lang, 'to_break')} <code>/substitution {escape(ciphertext)}</code>"
    )


def affine_encrypted(lang: str, a: int, b: int, ciphertext: str) -> str:
    body = _encrypted_template(lang, "✉️", "Affine", f"a={a}, b={b}", ciphertext)
    return f"{body}\n\n👉 {label(lang, 'to_break')} <code>/affine {escape(ciphertext)}</code>"


def rot_result(lang: str, name: str, text: str) -> str:
    return f"🔄 <b>{escape(name)}</b>\n———————————\n<code>{escape(text)}</code>"


def password_generated(lang: str, password: str) -> str:
    return (
        f"🔐 <b>{label(lang, 'new_password')}</b> <i>({len(password)} {label(lang, 'characters')})</i>\n"
        f"———————————\n<code>{escape(password)}</code>\n\n"
        f"<i>{label(lang, 'tap_to_copy')}</i>"
    )


def random_key_generated(lang: str, key: str) -> str:
    return f"🔑 <b>{label(lang, 'random_key')}</b> <code>{key}</code>"


def hash_result(lang: str, name: str, digest: str) -> str:
    return f"#️⃣ <b>{escape(name)}</b>\n———————————\n<code>{digest}</code>"


def base64_encoded(lang: str, encoded: str) -> str:
    return (
        f"🔡 <b>Base64</b>\n———————————\n<code>{escape(encoded)}</code>\n\n"
        f"👉 {label(lang, 'to_decode')} <code>/decode {escape(encoded)}</code>"
    )


def analysis_result(lang: str, analysis) -> str:
    top_letters = ", ".join(f"{letter}:{count}" for letter, count in analysis.top_letters) or "—"
    titles = {
        "uz": (
            "📊 <b>Matn tahlili</b>",
            "Uzunlik",
            "belgi",
            "harf",
            "Eng ko'p harflar",
            "✅ Ingliz tiliga o'xshaydi",
            "⚠️ Tasodifiy/shifrlangan ko'rinadi",
        ),
        "ru": (
            "📊 <b>Анализ текста</b>",
            "Длина",
            "символов",
            "букв",
            "Самые частые буквы",
            "✅ Похоже на английский",
            "⚠️ Выглядит случайным/зашифрованным",
        ),
        "en": (
            "📊 <b>Text analysis</b>",
            "Length",
            "characters",
            "letters",
            "Most frequent letters",
            "✅ Looks like English",
            "⚠️ Looks random/encrypted",
        ),
    }
    title, length_label, chars_label, letters_label, freq_label, verdict_yes, verdict_no = titles.get(
        lang, titles["uz"]
    )
    verdict = verdict_yes if analysis.looks_english else verdict_no
    return (
        f"{title}\n"
        "———————————\n"
        f"{length_label}: {analysis.length} {chars_label} ({analysis.letter_count} {letters_label})\n"
        f"Shannon entropy: {analysis.shannon_entropy_bits:.3f} bit\n"
        f"Index of Coincidence: {analysis.index_of_coincidence:.4f} <i>(English ≈ 0.0667)</i>\n"
        f"Chi-squared (vs. English): {analysis.chi_squared_vs_english:.1f}\n"
        f"{freq_label}: {top_letters}\n\n"
        f"{verdict}"
    )


def history_result(lang: str, jobs: list[tuple[str, str, str]]) -> str:
    titles = {
        "uz": ("📜 <b>Tarix</b>\n\nHali hech qanday so'rov yo'q.", "📜 <b>So'nggi so'rovlaringiz</b>\n\n"),
        "ru": ("📜 <b>История</b>\n\nПока нет запросов.", "📜 <b>Ваши последние запросы</b>\n\n"),
        "en": ("📜 <b>History</b>\n\nNo requests yet.", "📜 <b>Your recent requests</b>\n\n"),
    }
    empty_text, header = titles.get(lang, titles["uz"])
    if not jobs:
        return empty_text
    lines = [f"• <code>{job_type}</code> — {status} ({created_at})" for job_type, status, created_at in jobs]
    return header + "\n".join(lines)
