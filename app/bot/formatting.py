"""Message templates — kept separate from handlers.py so the "what the user
sees" layer can change without touching dispatch/validation logic."""

from __future__ import annotations

from html import escape

WELCOME_TEXT = """\
🔓 <b>Cryptanalysis Lab</b>

Kodlangan yoki shifrlangan matnni yuboring — <b>kalit shart emas</b>.

<b>Qo'llab-quvvatlanadi:</b>
• Base64 / Hex / URL-encoding — avtomatik aniqlanadi
• XOR, Vigenère, monoalfavit almashtirish — statistik tahlil orqali buziladi

Pastdagi tugmani bosing, so'ng matningizni oddiy xabar sifatida yuboring — buyruq yozish shart emas 👇
"""

HELP_TEXT = """\
🔓 <b>Cryptanalysis Lab — buyruqlar</b>

<b>Avtomatik dekodlash</b>
<code>/decode &lt;matn&gt;</code> — base64 / hex / url / binary zanjirini aniqlab ochadi

<b>Klassik shifrlarni buzish</b>
<code>/xor &lt;hex&gt;</code> — takrorlanuvchi kalitli XOR (kiritish <b>hex</b> formatida)
<code>/vigenere &lt;matn&gt;</code> — Kasiski testi + Index of Coincidence
<code>/substitution &lt;matn&gt;</code> — hill-climbing + quadgram statistikasi

Har bir so'rovga vaqt/CPU limiti qo'yilgan.
"""

_DETAIL_TEXTS = {
    "decode": (
        "📥 <b>Avtomatik dekodlash</b>\n\n"
        "Kodlangan matnni (base64, hex, URL-encoding, binary) avtomatik aniqlab, "
        "zanjirlab ochadi — CyberChef uslubida.\n\n"
        "<b>Foydalanish:</b>\n<code>/decode &lt;matn&gt;</code>\n\n"
        "<b>Misol:</b>\n<code>/decode c2VjdXJpdHkgaXMgaW1wb3J0YW50</code>"
    ),
    "xor": (
        "🔑 <b>XOR buzish</b>\n\n"
        "Noma'lum (takrorlanuvchi) kalit bilan XOR qilingan matnni kalitsiz buzadi. "
        "<b>Kiritish hex formatida bo'lishi kerak.</b>\n\n"
        "<b>Foydalanish:</b>\n<code>/xor &lt;hex_shifrmatn&gt;</code>\n\n"
        "<b>Misol:</b>\n<code>/xor 18212a6e3d3c262d27692d3c233e216e2a26376e263c22</code>"
    ),
    "vigenere": (
        "📜 <b>Vigenère buzish</b>\n\n"
        "Kasiski testi + Index of Coincidence yordamida kalit uzunligini, "
        "so'ng chastota tahlili bilan kalitning o'zini topadi.\n\n"
        "<b>Foydalanish:</b>\n<code>/vigenere &lt;shifrmatn&gt;</code>\n\n"
        "<b>Misol:</b>\n<code>/vigenere EPSUTAHBCGCSNZMCEWUELXVLDBFREKVRDJOPVBVBF</code>"
    ),
    "substitution": (
        "🔤 <b>Monoalfavit substitution buzish</b>\n\n"
        "Hill-climbing (quadgram statistikasi bilan) orqali harf-almashtirish "
        "jadvalini qayta tiklaydi.\n\n"
        "<b>Foydalanish:</b>\n<code>/substitution &lt;shifrmatn&gt;</code>\n\n"
        "<b>Misol:</b>\n<code>Rth tzdrale ay wlegraoljgte drlhrwthd fjwn rtacdjqid</code>"
    ),
    "encrypt": (
        "✉️ <b>Shifrlash (buzish emas — yaratish)</b>\n\n"
        "O'z matningizni shifrlab, keyin yuqoridagi buyruqlar bilan botning "
        "uni kalitsiz qanday buzishini sinab ko'ring.\n\n"
        "<code>/caesar &lt;shift&gt; &lt;matn&gt;</code>\n"
        "<code>/caesar 3 hello world</code>\n\n"
        "<code>/vigenere_encrypt &lt;kalit&gt; &lt;matn&gt;</code>\n"
        "<code>/vigenere_encrypt LION the quick brown fox</code>\n\n"
        "<code>/xor_encrypt &lt;kalit&gt; &lt;matn&gt;</code>\n"
        "<code>/xor_encrypt LION the quick brown fox</code> → natija <code>/xor</code>ga beriladi\n\n"
        "<code>/substitution_encrypt &lt;matn&gt;</code> — tasodifiy almashtirish bilan shifrlaydi"
    ),
}


def detail_text(command: str) -> str:
    return _DETAIL_TEXTS.get(command, HELP_TEXT)


ACTION_PROMPTS = {
    "decode": "📥 <b>Avtomatik dekodlash</b>\n\nKodlangan matningizni yuboring 👇",
    "xor": (
        "🔑 <b>XOR buzish</b>\n\nShifrmatnni <b>hex</b> formatida yuboring "
        "(masalan: <code>1a2b3c...</code>) 👇"
    ),
    "vigenere": "📜 <b>Vigenère buzish</b>\n\nShifrmatningizni yuboring 👇",
    "substitution": "🔤 <b>Substitution buzish</b>\n\nShifrmatningizni yuboring 👇",
    "caesar": (
        "🅰️ <b>Caesar shifrlash</b>\n\n"
        "<code>shift matn</code> formatida yuboring.\nMisol: <code>3 hello world</code> 👇"
    ),
    "vigenere_encrypt": (
        "📜 <b>Vigenère bilan shifrlash</b>\n\n"
        "<code>kalit matn</code> formatida yuboring.\nMisol: <code>LION the quick brown fox</code> 👇"
    ),
    "xor_encrypt": (
        "🔑 <b>XOR bilan shifrlash</b>\n\n"
        "<code>kalit matn</code> formatida yuboring.\nMisol: <code>LION the quick brown fox</code> 👇"
    ),
    "substitution_encrypt": "🔤 <b>Tasodifiy substitution bilan shifrlash</b>\n\nMatningizni yuboring 👇",
}


def decode_result(chain_desc: str, is_plaintext: bool, final_text: str) -> str:
    status = "✅ <b>Aniqlandi</b>" if is_plaintext else "⚠️ <b>To'liq ochilmadi</b>"
    return (
        f"📥 <b>Zanjir:</b> {escape(chain_desc)}\n"
        f"{status}\n"
        f"———————————\n"
        f"<code>{escape(final_text)}</code>"
    )


def xor_result(key_ascii: str, key_length: int, plaintext: str) -> str:
    return (
        f"🔑 <b>Kalit:</b> <code>{escape(key_ascii)}</code> "
        f"<i>({key_length} bayt)</i>\n"
        f"———————————\n"
        f"<code>{escape(plaintext)}</code>"
    )


def vigenere_result(key: str, plaintext: str) -> str:
    return (
        f"📜 <b>Kalit:</b> <code>{escape(key)}</code>\n"
        f"———————————\n"
        f"<code>{escape(plaintext)}</code>"
    )


def substitution_result(plaintext: str) -> str:
    return f"🔤 <b>Natija:</b>\n———————————\n<code>{escape(plaintext)}</code>"


def caesar_encrypted(shift: int, ciphertext: str) -> str:
    return (
        f"✉️ <b>Caesar shifrlandi</b> <i>(shift={shift})</i>\n"
        f"———————————\n<code>{escape(ciphertext)}</code>"
    )


def vigenere_encrypted(key: str, ciphertext: str) -> str:
    return (
        f"✉️ <b>Vigenère bilan shifrlandi</b> <i>(kalit: {escape(key)})</i>\n"
        f"———————————\n<code>{escape(ciphertext)}</code>\n\n"
        f"👉 Buzish uchun: <code>/vigenere {escape(ciphertext)}</code>"
    )


def xor_encrypted(key: str, ciphertext_hex: str) -> str:
    return (
        f"✉️ <b>XOR bilan shifrlandi</b> <i>(kalit: {escape(key)})</i>\n"
        f"———————————\n<code>{ciphertext_hex}</code>\n\n"
        f"👉 Buzish uchun: <code>/xor {ciphertext_hex}</code>"
    )


def substitution_encrypted(ciphertext: str) -> str:
    return (
        f"✉️ <b>Tasodifiy substitution bilan shifrlandi</b>\n"
        f"———————————\n<code>{escape(ciphertext)}</code>\n\n"
        f"👉 Buzish uchun: <code>/substitution {escape(ciphertext)}</code>"
    )
