"""Inline keyboards: a categorized main menu, each category opening a
submenu of specific tools. Tapping an action button sets an FSM state and
prompts the user for plain text — no slash command needed. See
handlers.py for the state handler. All button labels route through
app.bot.i18n so the same menu renders in uz/ru/en.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.i18n import LANGUAGE_NAMES, label


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


def _rows_of_two(buttons: list[tuple[str, str]]) -> list[list[InlineKeyboardButton]]:
    return [
        [InlineKeyboardButton(text=text, callback_data=data) for text, data in buttons[i : i + 2]]
        for i in range(0, len(buttons), 2)
    ]


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = _rows_of_two(_category_buttons(lang))
    rows.append(
        [
            InlineKeyboardButton(text=label(lang, "language"), callback_data="menu:language"),
            InlineKeyboardButton(text=label(lang, "help"), callback_data="menu:help"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def decode_break_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = _rows_of_two(_decode_break_buttons(lang))
    rows.append([InlineKeyboardButton(text=label(lang, "menu"), callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def encrypt_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = _rows_of_two(_encrypt_buttons(lang))
    rows.append([InlineKeyboardButton(text=label(lang, "menu"), callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def hash_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = _rows_of_two(_hash_buttons(lang))
    rows.append([InlineKeyboardButton(text=label(lang, "menu"), callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def keygen_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=text, callback_data=data)] for text, data in _keygen_buttons(lang)]
    rows.append([InlineKeyboardButton(text=label(lang, "menu"), callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def wordlists_menu_keyboard(lang: str, wordlists: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=wl["label"], callback_data=f"getfile:{wl['key']}")]
        for wl in wordlists
    ]
    rows.append([InlineKeyboardButton(text=label(lang, "menu"), callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def language_picker_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=name, callback_data=f"setlang:{code}")]
        for code, name in LANGUAGE_NAMES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def password_result_keyboard(lang: str, length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label(lang, "regenerate"), callback_data=f"genpass:{length}")],
            [InlineKeyboardButton(text=label(lang, "menu"), callback_data="menu:main")],
        ]
    )


def randkey_result_keyboard(lang: str, kind: str, length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=label(lang, "regenerate"), callback_data=f"randkey:{kind}:{length}"
                )
            ],
            [InlineKeyboardButton(text=label(lang, "menu"), callback_data="menu:main")],
        ]
    )


def cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label(lang, "cancel"), callback_data="menu:main")]]
    )


def back_to_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label(lang, "menu"), callback_data="menu:main")]]
    )
