"""Inline keyboards: a categorized main menu, each category opening a
submenu of specific tools. Tapping an action button sets an FSM state and
prompts the user for plain text — no slash command needed. See
handlers.py for the state handler. All button labels route through
app.bot.i18n so the same menu renders in uz/ru/en.

Buttons also carry a `style` ("primary" blue, "success" green, "danger"
red, or None for the client's neutral default) — supported by Telegram
clients released after 2026-02-09; older clients just show it unstyled.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.i18n import LANGUAGE_NAMES, label


def _btn(text: str, data: str, style: str | None = None) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data, style=style)


def _category_buttons(lang: str) -> list[tuple[str, str]]:
    return [
        (label(lang, "cat_decode"), "menu:decode_break"),
        (label(lang, "cat_encrypt"), "menu:encrypt"),
        (label(lang, "cat_auto_detector"), "action:decode"),
        (label(lang, "cat_analysis"), "action:analyze"),
        (label(lang, "cat_hash_tools"), "menu:hash"),
        (label(lang, "cat_file_tools"), "menu:wordlists"),
        (label(lang, "cat_key_generator"), "menu:keygen"),
        (label(lang, "cat_history"), "menu:history"),
    ]


def _decode_break_buttons(lang: str) -> list[tuple[str, str]]:
    return [
        (label(lang, "btn_xor"), "action:xor"),
        (label(lang, "btn_vigenere"), "action:vigenere"),
        (label(lang, "btn_substitution"), "action:substitution"),
        (label(lang, "btn_affine"), "action:affine"),
    ]


def _encrypt_buttons(lang: str) -> list[tuple[str, str]]:
    return [
        (label(lang, "btn_caesar"), "action:caesar"),
        (label(lang, "btn_vigenere"), "action:vigenere_encrypt"),
        (label(lang, "btn_xor"), "action:xor_encrypt"),
        (label(lang, "btn_substitution"), "action:substitution_encrypt"),
        (label(lang, "btn_affine"), "action:affine_encrypt"),
        (label(lang, "btn_rot13"), "action:rot13"),
        (label(lang, "btn_rot47"), "action:rot47"),
    ]


def _hash_buttons(lang: str) -> list[tuple[str, str]]:
    return [
        (label(lang, "btn_sha256"), "action:sha256"),
        (label(lang, "btn_sha1"), "action:sha1"),
        (label(lang, "btn_md5"), "action:md5"),
        (label(lang, "btn_base64"), "action:base64_encode"),
    ]


def _keygen_buttons(lang: str) -> list[tuple[str, str]]:
    return [
        (label(lang, "btn_strong_password"), "genpass:16"),
        (label(lang, "btn_random_key"), "randkey:alpha:8"),
        (label(lang, "btn_personal_wordlist"), "action:personal_wordlist"),
    ]


def _rows_of_two(buttons: list[tuple[str, str]], style: str | None) -> list[list[InlineKeyboardButton]]:
    return [
        [_btn(text, data, style) for text, data in buttons[i : i + 2]]
        for i in range(0, len(buttons), 2)
    ]


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    # "Decode" opens the cipher-breaking submenu (buzish) — red. Everything
    # else (opening/unwrapping encodings, analysis, utilities) stays blue.
    styles = {"menu:decode_break": "danger"}
    categories = [(text, data, styles.get(data, "primary")) for text, data in _category_buttons(lang)]
    rows = [
        [_btn(text, data, style) for text, data, style in categories[i : i + 2]]
        for i in range(0, len(categories), 2)
    ]
    rows.append(
        [
            _btn(label(lang, "language"), "menu:language"),
            _btn(label(lang, "help"), "menu:help"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def decode_break_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    # These are the actual cipher-breaking actions (buzish) — red.
    rows = _rows_of_two(_decode_break_buttons(lang), "danger")
    rows.append([_btn(label(lang, "menu"), "menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def encrypt_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = _rows_of_two(_encrypt_buttons(lang), "primary")
    rows.append([_btn(label(lang, "menu"), "menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def hash_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = _rows_of_two(_hash_buttons(lang), "primary")
    rows.append([_btn(label(lang, "menu"), "menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def keygen_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [[_btn(text, data, "success")] for text, data in _keygen_buttons(lang)]
    rows.append([_btn(label(lang, "menu"), "menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def wordlists_menu_keyboard(lang: str, wordlists: list[dict]) -> InlineKeyboardMarkup:
    rows = [[_btn(wl["label"], f"getfile:{wl['key']}", "primary")] for wl in wordlists]
    rows.append([_btn(label(lang, "menu"), "menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def language_picker_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [_btn(name, f"setlang:{code}", "primary")] for code, name in LANGUAGE_NAMES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def password_result_keyboard(lang: str, length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn(label(lang, "regenerate"), f"genpass:{length}", "success")],
            [_btn(label(lang, "menu"), "menu:main")],
        ]
    )


def randkey_result_keyboard(lang: str, kind: str, length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn(label(lang, "regenerate"), f"randkey:{kind}:{length}", "success")],
            [_btn(label(lang, "menu"), "menu:main")],
        ]
    )


def cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[_btn(label(lang, "cancel"), "menu:main", "danger")]])


def back_to_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[_btn(label(lang, "menu"), "menu:main")]])
