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

Boshlash uchun pastdagi tugmalardan birini tanlang 👇
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
}


def detail_text(command: str) -> str:
    return _DETAIL_TEXTS.get(command, HELP_TEXT)


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
