"""Inline keyboards for the main menu and per-command help screens."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

MENU_BUTTONS = [
    ("🔓 Decode", "menu:decode"),
    ("🔑 XOR", "menu:xor"),
    ("📜 Vigenère", "menu:vigenere"),
    ("🔤 Substitution", "menu:substitution"),
]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=data) for label, data in MENU_BUTTONS[i : i + 2]]
        for i in range(0, len(MENU_BUTTONS), 2)
    ]
    rows.append([InlineKeyboardButton(text="❓ Yordam", callback_data="menu:help")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")]]
    )
