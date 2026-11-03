"""Inline keyboards for the main menu and the "tap, then just type" flow.

Tapping an action button sets an FSM state and prompts the user for plain
text — no slash command needed. See handlers.py for the state handler.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

BREAK_BUTTONS = [
    ("🔓 Decode", "action:decode"),
    ("🔑 XOR buzish", "action:xor"),
    ("📜 Vigenère buzish", "action:vigenere"),
    ("🔤 Substitution buzish", "action:substitution"),
]

ENCRYPT_BUTTONS = [
    ("🅰️ Caesar", "action:caesar"),
    ("📜 Vigenère", "action:vigenere_encrypt"),
    ("🔑 XOR", "action:xor_encrypt"),
    ("🔤 Substitution", "action:substitution_encrypt"),
    ("#️⃣ SHA-256", "action:sha256"),
    ("#️⃣ SHA-1", "action:sha1"),
    ("#️⃣ MD5", "action:md5"),
    ("🔡 Base64", "action:base64_encode"),
]


def _rows_of_two(buttons: list[tuple[str, str]]) -> list[list[InlineKeyboardButton]]:
    return [
        [InlineKeyboardButton(text=label, callback_data=data) for label, data in buttons[i : i + 2]]
        for i in range(0, len(buttons), 2)
    ]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = _rows_of_two(BREAK_BUTTONS)
    rows.append([InlineKeyboardButton(text="✉️ Shifrlash", callback_data="menu:encrypt")])
    rows.append([InlineKeyboardButton(text="📋 Top wordlistlar", callback_data="menu:wordlists")])
    rows.append([InlineKeyboardButton(text="❓ Yordam", callback_data="menu:help")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def wordlists_menu_keyboard(wordlists: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=wl["label"], callback_data=f"getfile:{wl['key']}")]
        for wl in wordlists
    ]
    rows.append([InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def encrypt_menu_keyboard() -> InlineKeyboardMarkup:
    rows = _rows_of_two(ENCRYPT_BUTTONS)
    rows.append([InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="menu:main")]]
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")]]
    )
