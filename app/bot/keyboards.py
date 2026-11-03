"""Inline keyboards: a categorized main menu, each category opening a
submenu of specific tools. Tapping an action button sets an FSM state and
prompts the user for plain text — no slash command needed. See
handlers.py for the state handler.
"""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

CATEGORY_BUTTONS = [
    ("🔓 Decode", "menu:decode_break"),
    ("🔒 Encrypt", "menu:encrypt"),
    ("🔍 Auto Detector", "action:decode"),
    ("📊 Analysis", "action:analyze"),
    ("#️⃣ Hash Tools", "menu:hash"),
    ("📁 File Tools", "menu:wordlists"),
    ("🔑 Key Generator", "menu:keygen"),
    ("🕐 History", "menu:history"),
]

DECODE_BREAK_BUTTONS = [
    ("🔑 XOR", "action:xor"),
    ("📜 Vigenère", "action:vigenere"),
    ("🔤 Substitution", "action:substitution"),
    ("🔢 Affine", "action:affine"),
]

ENCRYPT_BUTTONS = [
    ("🅰️ Caesar", "action:caesar"),
    ("📜 Vigenère", "action:vigenere_encrypt"),
    ("🔑 XOR", "action:xor_encrypt"),
    ("🔤 Substitution", "action:substitution_encrypt"),
    ("🔢 Affine", "action:affine_encrypt"),
    ("🔄 ROT13", "action:rot13"),
    ("🔄 ROT47", "action:rot47"),
]

HASH_BUTTONS = [
    ("#️⃣ SHA-256", "action:sha256"),
    ("#️⃣ SHA-1", "action:sha1"),
    ("#️⃣ MD5", "action:md5"),
    ("🔡 Base64", "action:base64_encode"),
]

KEYGEN_BUTTONS = [
    ("🔐 Kuchli parol", "genpass:16"),
    ("🔑 Tasodifiy kalit", "randkey:alpha:8"),
    ("📝 Shaxsiy wordlist", "action:personal_wordlist"),
]


def _rows_of_two(buttons: list[tuple[str, str]]) -> list[list[InlineKeyboardButton]]:
    return [
        [InlineKeyboardButton(text=label, callback_data=data) for label, data in buttons[i : i + 2]]
        for i in range(0, len(buttons), 2)
    ]


def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = _rows_of_two(CATEGORY_BUTTONS)
    rows.append([InlineKeyboardButton(text="❓ Yordam", callback_data="menu:help")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def decode_break_menu_keyboard() -> InlineKeyboardMarkup:
    rows = _rows_of_two(DECODE_BREAK_BUTTONS)
    rows.append([InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def encrypt_menu_keyboard() -> InlineKeyboardMarkup:
    rows = _rows_of_two(ENCRYPT_BUTTONS)
    rows.append([InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def hash_menu_keyboard() -> InlineKeyboardMarkup:
    rows = _rows_of_two(HASH_BUTTONS)
    rows.append([InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def keygen_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=label, callback_data=data)] for label, data in KEYGEN_BUTTONS]
    rows.append([InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def wordlists_menu_keyboard(wordlists: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=wl["label"], callback_data=f"getfile:{wl['key']}")]
        for wl in wordlists
    ]
    rows.append([InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def password_result_keyboard(length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangisini", callback_data=f"genpass:{length}")],
            [InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")],
        ]
    )


def randkey_result_keyboard(kind: str, length: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangisini", callback_data=f"randkey:{kind}:{length}")],
            [InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")],
        ]
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="menu:main")]]
    )


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Menyu", callback_data="menu:main")]]
    )
