"""Message templates — kept separate from handlers.py so the "what the user
sees" layer can change without touching dispatch/validation logic."""

from __future__ import annotations

from html import escape

WELCOME_TEXT = """\
🔓 <b>Cryptanalysis Bot</b>

Men ikki narsani qilaman:

<b>🔨 Buzish</b> - kodlangan/shifrlangan matnni <b>kalitsiz</b> ochaman
(Base64, Hex, URL-encoding, XOR, Vigenère, monoalfavit almashtirish)

<b>✉️ Qurish</b> - o'z matningizni klassik shifrlar bilan shifrlab beraman,
keyin uni qayta buzishimni sinab ko'rasiz

Pastdagi tugmani bosing, so'ng matningizni oddiy xabar sifatida yuboring - buyruq yozish shart emas 👇
"""

HELP_TEXT = """\
🔓 <b>Cryptanalysis Bot - buyruqlar</b>

<b>🔨 Buzish</b>
<code>/decode &lt;matn&gt;</code> - base64 / hex / url / binary zanjirini aniqlab ochadi
<code>/xor &lt;hex&gt;</code> - takrorlanuvchi kalitli XOR (kiritish <b>hex</b> formatida)
<code>/vigenere &lt;matn&gt;</code> - Kasiski testi + Index of Coincidence
<code>/substitution &lt;matn&gt;</code> - hill-climbing + quadgram statistikasi

<b>✉️ Qurish (shifrlash)</b>
<code>/caesar &lt;shift&gt; &lt;matn&gt;</code>
<code>/vigenere_encrypt &lt;kalit&gt; &lt;matn&gt;</code>
<code>/xor_encrypt &lt;kalit&gt; &lt;matn&gt;</code>
<code>/substitution_encrypt &lt;matn&gt;</code>
<code>/sha256 /sha1 /md5 /base64_encode &lt;matn&gt;</code>

Har bir so'rovga vaqt/CPU limiti qo'yilgan.
"""

_DETAIL_TEXTS = {
    "decode": (
        "📥 <b>Avtomatik dekodlash</b>\n\n"
        "Kodlangan matnni (base64, hex, URL-encoding, binary) avtomatik aniqlab, "
        "zanjirlab ochadi - CyberChef uslubida.\n\n"
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
        "✉️ <b>Qurish (shifrlash)</b>\n\n"
        "O'z matningizni shifrlab, keyin yuqoridagi buyruqlar bilan botning "
        "uni kalitsiz qanday buzishini sinab ko'ring.\n\n"
        "<code>/caesar &lt;shift&gt; &lt;matn&gt;</code>\n"
        "<code>/caesar 3 hello world</code>\n\n"
        "<code>/vigenere_encrypt &lt;kalit&gt; &lt;matn&gt;</code>\n"
        "<code>/vigenere_encrypt LION the quick brown fox</code>\n\n"
        "<code>/xor_encrypt &lt;kalit&gt; &lt;matn&gt;</code>\n"
        "<code>/xor_encrypt LION the quick brown fox</code> → natija <code>/xor</code>ga beriladi\n\n"
        "<code>/substitution_encrypt &lt;matn&gt;</code> - tasodifiy almashtirish bilan shifrlaydi\n\n"
        "<b>Hash / kodlash:</b>\n"
        "<code>/sha256 &lt;matn&gt;</code>, <code>/sha1 &lt;matn&gt;</code>, "
        "<code>/md5 &lt;matn&gt;</code>, <code>/base64_encode &lt;matn&gt;</code>"
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
    "sha256": "#️⃣ <b>SHA-256 hash</b>\n\nMatningizni yuboring 👇",
    "sha1": "#️⃣ <b>SHA-1 hash</b>\n\nMatningizni yuboring 👇",
    "md5": "#️⃣ <b>MD5 hash</b>\n\nMatningizni yuboring 👇",
    "base64_encode": "🔡 <b>Base64 kodlash</b>\n\nMatningizni yuboring 👇",
}


def decode_result(chain_desc: str, is_plaintext: bool, final_text: str) -> str:
    status = "✅ <b>Aniqlandi</b>" if is_plaintext else "⚠️ <b>To'liq ochilmadi</b>"
    return (
        f"📥 <b>Zanjir:</b> {escape(chain_desc)}\n"
        f"{status}\n"
        f"-——————————\n"
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


WORDLIST_FILES = [
    {
        "key": "wl_top10k",
        "label": "🥇 Top 10 000",
        "name": "10k-most-common.txt",
        "size": "73 KB",
        "description": "Eng ko'p ishlatiladigan 10 000 parol — tezkor CTF uchun",
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
        "description": "Buyuk Britaniya NCSC rasmiy nashr etgan 100 000 eng zaif parol",
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
        "description": "Pwdb loyihasining 1 million eng ko'p uchraydigan paroli",
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
        "description": "Tarixdagi eng ko'p tanqid qilingan 500 ta zaif parol",
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
        "description": "xato.net'ning to'liq 10 milliondan iborat parollar bazasi",
        "url": (
            "https://raw.githubusercontent.com/danielmiessler/SecLists/"
            "master/Passwords/Common-Credentials/xato-net-10-million-passwords.txt"
        ),
    },
]

WORDLISTS_TEXT = """\
📋 <b>Dunyodagi top 5 wordlist</b>

Har biri SecLists (xavfsizlik tadqiqotchilari eng ko'p ishlatadigan ochiq \
to'plam) dan — tugmani bosing, fayl to'g'ridan-to'g'ri shu yerga yuboriladi.

⚠️ <i>Faqat ruxsat etilgan pentest, CTF yoki xavfsizlik tadqiqoti uchun ishlating.</i>
"""


def substitution_encrypted(ciphertext: str) -> str:
    return (
        f"✉️ <b>Tasodifiy substitution bilan shifrlandi</b>\n"
        f"———————————\n<code>{escape(ciphertext)}</code>\n\n"
        f"👉 Buzish uchun: <code>/substitution {escape(ciphertext)}</code>"
    )


def hash_result(label: str, digest: str) -> str:
    return f"#️⃣ <b>{escape(label)}</b>\n———————————\n<code>{digest}</code>"


def base64_encoded(encoded: str) -> str:
    return (
        f"🔡 <b>Base64</b>\n———————————\n<code>{escape(encoded)}</code>\n\n"
        f"👉 Ochish uchun: <code>/decode {escape(encoded)}</code>"
    )
