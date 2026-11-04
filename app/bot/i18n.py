"""Central translation table (uz / ru / en). Every user-facing string in
the bot goes through t(lang, key, **kwargs) or one of the per-language
dicts below — no translatable text should live directly in formatting.py,
keyboards.py or handlers.py.
"""

from __future__ import annotations

SUPPORTED_LANGUAGES = ("uz", "ru", "en")
DEFAULT_LANGUAGE = "uz"

LANGUAGE_NAMES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

# ── Short labels (buttons, inline words used inside result templates) ──

LABELS = {
    "menu": {"uz": "⬅️ Menyu", "ru": "⬅️ Меню", "en": "⬅️ Menu"},
    "help": {"uz": "❓ Yordam", "ru": "❓ Помощь", "en": "❓ Help"},
    "cancel": {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"},
    "regenerate": {"uz": "🔄 Yangisini", "ru": "🔄 Новый", "en": "🔄 New one"},
    "language": {"uz": "🌐 Til", "ru": "🌐 Язык", "en": "🌐 Language"},
    "cat_decode": {"uz": "🔓 Decode", "ru": "🔓 Decode", "en": "🔓 Decode"},
    "cat_encrypt": {"uz": "🔒 Encrypt", "ru": "🔒 Encrypt", "en": "🔒 Encrypt"},
    "cat_auto_detector": {
        "uz": "🔍 Auto Detector",
        "ru": "🔍 Auto Detector",
        "en": "🔍 Auto Detector",
    },
    "cat_analysis": {"uz": "📊 Analysis", "ru": "📊 Analysis", "en": "📊 Analysis"},
    "cat_hash_tools": {"uz": "#️⃣ Hash Tools", "ru": "#️⃣ Hash Tools", "en": "#️⃣ Hash Tools"},
    "cat_file_tools": {"uz": "📁 File Tools", "ru": "📁 File Tools", "en": "📁 File Tools"},
    "cat_key_generator": {
        "uz": "🔑 Key Generator",
        "ru": "🔑 Key Generator",
        "en": "🔑 Key Generator",
    },
    "cat_history": {"uz": "🕐 History", "ru": "🕐 History", "en": "🕐 History"},
    "btn_xor": {"uz": "🔑 XOR", "ru": "🔑 XOR", "en": "🔑 XOR"},
    "btn_vigenere": {"uz": "📜 Vigenère", "ru": "📜 Vigenère", "en": "📜 Vigenère"},
    "btn_substitution": {
        "uz": "🔤 Substitution",
        "ru": "🔤 Substitution",
        "en": "🔤 Substitution",
    },
    "btn_affine": {"uz": "🔢 Affine", "ru": "🔢 Affine", "en": "🔢 Affine"},
    "btn_caesar": {"uz": "🅰️ Caesar", "ru": "🅰️ Caesar", "en": "🅰️ Caesar"},
    "btn_rot13": {"uz": "🔄 ROT13", "ru": "🔄 ROT13", "en": "🔄 ROT13"},
    "btn_rot47": {"uz": "🔄 ROT47", "ru": "🔄 ROT47", "en": "🔄 ROT47"},
    "btn_sha256": {"uz": "#️⃣ SHA-256", "ru": "#️⃣ SHA-256", "en": "#️⃣ SHA-256"},
    "btn_sha1": {"uz": "#️⃣ SHA-1", "ru": "#️⃣ SHA-1", "en": "#️⃣ SHA-1"},
    "btn_md5": {"uz": "#️⃣ MD5", "ru": "#️⃣ MD5", "en": "#️⃣ MD5"},
    "btn_base64": {"uz": "🔡 Base64", "ru": "🔡 Base64", "en": "🔡 Base64"},
    "btn_strong_password": {
        "uz": "🔐 Kuchli parol",
        "ru": "🔐 Надёжный пароль",
        "en": "🔐 Strong password",
    },
    "btn_random_key": {
        "uz": "🔑 Tasodifiy kalit",
        "ru": "🔑 Случайный ключ",
        "en": "🔑 Random key",
    },
    "btn_personal_wordlist": {
        "uz": "📝 Shaxsiy wordlist",
        "ru": "📝 Личный wordlist",
        "en": "📝 Personal wordlist",
    },
    "status_detected": {"uz": "✅ Aniqlandi", "ru": "✅ Определено", "en": "✅ Detected"},
    "status_not_decoded": {
        "uz": "⚠️ To'liq ochilmadi",
        "ru": "⚠️ Не раскрыто полностью",
        "en": "⚠️ Not fully decoded",
    },
    "chain": {"uz": "Zanjir:", "ru": "Цепочка:", "en": "Chain:"},
    "key": {"uz": "Kalit:", "ru": "Ключ:", "en": "Key:"},
    "result": {"uz": "Natija:", "ru": "Результат:", "en": "Result:"},
    "bytes": {"uz": "bayt", "ru": "байт", "en": "bytes"},
    "characters": {"uz": "belgi", "ru": "символов", "en": "characters"},
    "to_break": {"uz": "Buzish uchun:", "ru": "Чтобы взломать:", "en": "To break:"},
    "to_decode": {"uz": "Ochish uchun:", "ru": "Чтобы раскрыть:", "en": "To decode:"},
    "tap_to_copy": {
        "uz": "Nusxalash uchun matnga bosing.",
        "ru": "Нажмите на текст, чтобы скопировать.",
        "en": "Tap the text to copy.",
    },
    "key_not_found": {
        "uz": "🤷 Kalit topilmadi.",
        "ru": "🤷 Ключ не найден.",
        "en": "🤷 Key not found.",
    },
    "new_password": {"uz": "Yangi parol", "ru": "Новый пароль", "en": "New password"},
    "random_key": {"uz": "Tasodifiy kalit:", "ru": "Случайный ключ:", "en": "Random key:"},
    "encrypted_with": {
        "uz": "shifrlandi",
        "ru": "зашифровано с помощью",
        "en": "encrypted with",
    },
    "visual_view": {
        "uz": "🌐 Vizual ko'rish",
        "ru": "🌐 Визуальный вид",
        "en": "🌐 Visual view",
    },
    "not_found": {"uz": "Topilmadi.", "ru": "Не найдено.", "en": "Not found."},
    "loading": {"uz": "Yuklanmoqda...", "ru": "Загрузка...", "en": "Loading..."},
    "source_label": {"uz": "Manba:", "ru": "Источник:", "en": "Source:"},
    "words_generated": {
        "uz": "ta so'z generatsiya qilindi.",
        "ru": "слов сгенерировано.",
        "en": "words generated.",
    },
    "enter_name": {
        "uz": "Iltimos, ismni kiriting:",
        "ru": "Пожалуйста, введите имя:",
        "en": "Please enter a name:",
    },
    "need_at_least_one_word": {
        "uz": "Hech bo'lmasa bitta so'z kerak edi.",
        "ru": "Нужно было хотя бы одно слово.",
        "en": "At least one word was needed.",
    },
    "wordlist_step1": {
        "uz": "🎯 <b>Shaxsiy wordlist generatori</b>\n\n1/4: <b>Ismni</b> kiriting:",
        "ru": "🎯 <b>Генератор личного wordlist</b>\n\n1/4: Введите <b>имя</b>:",
        "en": "🎯 <b>Personal wordlist generator</b>\n\n1/4: Enter a <b>name</b>:",
    },
    "wordlist_step2": {
        "uz": "2/4: <b>Taxallus/nickname</b> bo'lsa yozing, bo'lmasa <code>-</code> yuboring:",
        "ru": "2/4: Если есть <b>прозвище/никнейм</b> — напишите, иначе отправьте <code>-</code>:",
        "en": "2/4: If there's a <b>nickname</b>, send it, otherwise send <code>-</code>:",
    },
    "wordlist_step3": {
        "uz": (
            "3/4: <b>Tug'ilgan yil</b> (4 xonali, masalan 1995) bo'lsa yozing, "
            "bo'lmasa <code>-</code> yuboring:"
        ),
        "ru": (
            "3/4: Если есть <b>год рождения</b> (4 цифры, напр. 1995) — "
            "напишите, иначе отправьте <code>-</code>:"
        ),
        "en": (
            "3/4: If there's a <b>birth year</b> (4 digits, e.g. 1995), send it, "
            "otherwise send <code>-</code>:"
        ),
    },
    "wordlist_step3_error": {
        "uz": "Yil 4 xonali raqam bo'lishi kerak (masalan 1995) yoki <code>-</code> yuboring:",
        "ru": "Год должен быть 4-значным числом (напр. 1995) или отправьте <code>-</code>:",
        "en": "The year must be 4 digits (e.g. 1995), or send <code>-</code>:",
    },
    "wordlist_step4": {
        "uz": "4/4: Yana bir so'z (uy hayvoni, sevimli narsa) bo'lsa yozing, bo'lmasa <code>-</code>:",
        "ru": (
            "4/4: Если есть ещё слово (питомец, любимая вещь) — напишите, "
            "иначе отправьте <code>-</code>:"
        ),
        "en": (
            "4/4: If there's another word (pet, favorite thing), send it, "
            "otherwise send <code>-</code>:"
        ),
    },
    "shift_must_be_integer": {
        "uz": "shift butun son bo'lishi kerak",
        "ru": "сдвиг должен быть целым числом",
        "en": "shift must be an integer",
    },
    "key_letters_only": {
        "uz": "kalit faqat harflardan iborat bo'lishi kerak",
        "ru": "ключ должен состоять только из букв",
        "en": "key must consist of letters only",
    },
    "ab_must_be_integers": {
        "uz": "a va b butun son bo'lishi kerak",
        "ru": "a и b должны быть целыми числами",
        "en": "a and b must be integers",
    },
    "need_at_least_one_name": {
        "uz": "kamida bitta so'z (ism) kiriting",
        "ru": "введите хотя бы одно слово (имя)",
        "en": "enter at least one word (a name)",
    },
    "pruned_jobs": {
        "uz": "📊 Tozalangan eski job yozuvlari:",
        "ru": "📊 Удалено старых записей о заданиях:",
        "en": "📊 Pruned old job records:",
    },
    "audit_log_intact": {
        "uz": "✅ Audit log yaxlit.",
        "ru": "✅ Журнал аудита не нарушен.",
        "en": "✅ Audit log is intact.",
    },
    "audit_log_broken": {
        "uz": "🚨 Audit log buzilgan!",
        "ru": "🚨 Журнал аудита нарушен!",
        "en": "🚨 Audit log has been tampered with!",
    },
}

LANGUAGE_PICKER_TEXT = {
    "uz": "🌐 Tilni tanlang:",
    "ru": "🌐 Выберите язык:",
    "en": "🌐 Choose your language:",
}

LANGUAGE_SET_CONFIRM = {
    "uz": "✅ Til o'zbekcha qilib o'rnatildi.",
    "ru": "✅ Язык установлен на русский.",
    "en": "✅ Language set to English.",
}

GENERIC_ERROR = {
    "uz": "⚠️ Xatolik yuz berdi. Keyinroq qaytadan urinib ko'ring.",
    "ru": "⚠️ Произошла ошибка. Попробуйте ещё раз позже.",
    "en": "⚠️ Something went wrong. Please try again later.",
}

RATE_LIMITED = {
    "uz": "⏳ Juda ko'p so'rov. Birozdan keyin qayta urinib ko'ring.",
    "ru": "⏳ Слишком много запросов. Повторите попытку чуть позже.",
    "en": "⏳ Too many requests. Please try again shortly.",
}

ADMIN_ONLY = {
    "uz": "Bu buyruq faqat adminlar uchun.",
    "ru": "Эта команда доступна только администраторам.",
    "en": "This command is for admins only.",
}

STRAY_TEXT = {
    "uz": "🤔 Qaysi amalni bajarishni bilmadim. Tugmalardan birini tanlang:",
    "ru": "🤔 Не понял, что нужно сделать. Выберите действие из кнопок:",
    "en": "🤔 I'm not sure what to do with that. Please pick an option below:",
}

WELCOME_TEXT = {
    "uz": (
        "🔒 <b>DecodeWizard</b>\n<i>Cryptography &amp; Cryptanalysis Toolkit</i>\n\n"
        "Pastdagi bo'limdan birini tanlang, so'ng matningizni oddiy xabar sifatida "
        "yuboring - buyruq yozish shart emas 👇"
    ),
    "ru": (
        "🔒 <b>DecodeWizard</b>\n<i>Cryptography &amp; Cryptanalysis Toolkit</i>\n\n"
        "Выберите раздел ниже, затем просто отправьте текст обычным сообщением - "
        "вводить команду не обязательно 👇"
    ),
    "en": (
        "🔒 <b>DecodeWizard</b>\n<i>Cryptography &amp; Cryptanalysis Toolkit</i>\n\n"
        "Pick a category below, then just send your text as a plain message - "
        "no command needed 👇"
    ),
}

HELP_TEXT = {
    "uz": (
        "🔓 <b>DecodeWizard Bot - buyruqlar</b>\n\n"
        "<b>🔨 Buzish</b>\n"
        "<code>/decode &lt;matn&gt;</code> - base64/hex/url/binary zanjirini aniqlab ochadi\n"
        "<code>/xor &lt;hex&gt;</code> - takrorlanuvchi kalitli XOR (hex formatida)\n"
        "<code>/vigenere &lt;matn&gt;</code> - Kasiski testi + Index of Coincidence\n"
        "<code>/substitution &lt;matn&gt;</code> - hill-climbing + quadgram statistikasi\n"
        "<code>/affine &lt;matn&gt;</code> - barcha (a,b) juftligini sinab buzadi\n\n"
        "<b>✉️ Qurish (shifrlash)</b>\n"
        "<code>/caesar &lt;shift&gt; &lt;matn&gt;</code>\n"
        "<code>/vigenere_encrypt &lt;kalit&gt; &lt;matn&gt;</code>\n"
        "<code>/xor_encrypt &lt;kalit&gt; &lt;matn&gt;</code>\n"
        "<code>/substitution_encrypt &lt;matn&gt;</code>\n"
        "<code>/affine_encrypt &lt;a&gt; &lt;b&gt; &lt;matn&gt;</code>\n"
        "<code>/rot13 /rot47 &lt;matn&gt;</code>\n"
        "<code>/sha256 /sha1 /md5 /base64_encode &lt;matn&gt;</code>\n\n"
        "<b>🔬 Tahlil va vositalar</b>\n"
        "<code>/analyze &lt;matn&gt;</code> - entropiya, IoC, chastota\n"
        "<code>/history</code> - so'nggi so'rovlaringiz\n"
        "<code>/randkey [alpha|hex] [uzunlik]</code> - tasodifiy kalit\n"
        "<code>/genpass [uzunlik]</code> - kuchli parol\n"
        "<code>/language</code> - tilni o'zgartirish\n\n"
        "Har bir so'rovga vaqt/CPU limiti qo'yilgan."
    ),
    "ru": (
        "🔓 <b>DecodeWizard Bot - команды</b>\n\n"
        "<b>🔨 Взлом</b>\n"
        "<code>/decode &lt;текст&gt;</code> - автоопределение и раскрытие base64/hex/url/binary\n"
        "<code>/xor &lt;hex&gt;</code> - повторяющийся ключ XOR (в формате hex)\n"
        "<code>/vigenere &lt;текст&gt;</code> - тест Касиски + индекс совпадений\n"
        "<code>/substitution &lt;текст&gt;</code> - hill-climbing + статистика квадграмм\n"
        "<code>/affine &lt;текст&gt;</code> - перебор всех пар (a,b)\n\n"
        "<b>✉️ Шифрование</b>\n"
        "<code>/caesar &lt;сдвиг&gt; &lt;текст&gt;</code>\n"
        "<code>/vigenere_encrypt &lt;ключ&gt; &lt;текст&gt;</code>\n"
        "<code>/xor_encrypt &lt;ключ&gt; &lt;текст&gt;</code>\n"
        "<code>/substitution_encrypt &lt;текст&gt;</code>\n"
        "<code>/affine_encrypt &lt;a&gt; &lt;b&gt; &lt;текст&gt;</code>\n"
        "<code>/rot13 /rot47 &lt;текст&gt;</code>\n"
        "<code>/sha256 /sha1 /md5 /base64_encode &lt;текст&gt;</code>\n\n"
        "<b>🔬 Анализ и инструменты</b>\n"
        "<code>/analyze &lt;текст&gt;</code> - энтропия, IoC, частоты\n"
        "<code>/history</code> - ваши последние запросы\n"
        "<code>/randkey [alpha|hex] [длина]</code> - случайный ключ\n"
        "<code>/genpass [длина]</code> - надёжный пароль\n"
        "<code>/language</code> - сменить язык\n\n"
        "На каждый запрос установлен лимит времени/CPU."
    ),
    "en": (
        "🔓 <b>DecodeWizard Bot - commands</b>\n\n"
        "<b>🔨 Breaking</b>\n"
        "<code>/decode &lt;text&gt;</code> - auto-detects and unwraps base64/hex/url/binary\n"
        "<code>/xor &lt;hex&gt;</code> - repeating-key XOR (input in hex)\n"
        "<code>/vigenere &lt;text&gt;</code> - Kasiski test + Index of Coincidence\n"
        "<code>/substitution &lt;text&gt;</code> - hill-climbing + quadgram statistics\n"
        "<code>/affine &lt;text&gt;</code> - brute-forces every (a,b) pair\n\n"
        "<b>✉️ Encrypting</b>\n"
        "<code>/caesar &lt;shift&gt; &lt;text&gt;</code>\n"
        "<code>/vigenere_encrypt &lt;key&gt; &lt;text&gt;</code>\n"
        "<code>/xor_encrypt &lt;key&gt; &lt;text&gt;</code>\n"
        "<code>/substitution_encrypt &lt;text&gt;</code>\n"
        "<code>/affine_encrypt &lt;a&gt; &lt;b&gt; &lt;text&gt;</code>\n"
        "<code>/rot13 /rot47 &lt;text&gt;</code>\n"
        "<code>/sha256 /sha1 /md5 /base64_encode &lt;text&gt;</code>\n\n"
        "<b>🔬 Analysis &amp; tools</b>\n"
        "<code>/analyze &lt;text&gt;</code> - entropy, IoC, letter frequency\n"
        "<code>/history</code> - your recent requests\n"
        "<code>/randkey [alpha|hex] [length]</code> - random key\n"
        "<code>/genpass [length]</code> - strong password\n"
        "<code>/language</code> - change language\n\n"
        "Every request has a time/CPU limit."
    ),
}

DECODE_BREAK_MENU_TEXT = {
    "uz": "🔓 <b>Decode</b>\n\nQaysi shifrni buzishni xohlaysiz?",
    "ru": "🔓 <b>Decode</b>\n\nКакой шифр хотите взломать?",
    "en": "🔓 <b>Decode</b>\n\nWhich cipher would you like to break?",
}

HASH_MENU_TEXT = {
    "uz": "#️⃣ <b>Hash Tools</b>\n\nQaysi hash/kodlashni hisoblaymiz?",
    "ru": "#️⃣ <b>Hash Tools</b>\n\nКакой hash/кодирование посчитать?",
    "en": "#️⃣ <b>Hash Tools</b>\n\nWhich hash/encoding would you like?",
}

KEYGEN_MENU_TEXT = {
    "uz": "🔑 <b>Key Generator</b>\n\nNimani yaratamiz?",
    "ru": "🔑 <b>Key Generator</b>\n\nЧто создать?",
    "en": "🔑 <b>Key Generator</b>\n\nWhat would you like to generate?",
}

WORDLISTS_TEXT = {
    "uz": (
        "📋 <b>Dunyodagi top 5 wordlist</b>\n\n"
        "Har biri SecLists (xavfsizlik tadqiqotchilari eng ko'p ishlatadigan ochiq "
        "to'plam) dan - tugmani bosing, fayl to'g'ridan-to'g'ri shu yerga yuboriladi.\n\n"
        "⚠️ <i>Faqat ruxsat etilgan pentest, CTF yoki xavfsizlik tadqiqoti uchun ishlating.</i>"
    ),
    "ru": (
        "📋 <b>Топ-5 wordlist в мире</b>\n\n"
        "Каждый из SecLists (открытый набор, которым чаще всего пользуются "
        "исследователи безопасности) - нажмите кнопку, файл придёт прямо сюда.\n\n"
        "⚠️ <i>Используйте только для санкционированного пентеста, CTF или "
        "исследований безопасности.</i>"
    ),
    "en": (
        "📋 <b>Top 5 wordlists in the world</b>\n\n"
        "Each one comes from SecLists (the open collection security researchers "
        "use most) - tap a button and the file is sent right here.\n\n"
        "⚠️ <i>Use only for authorized pentesting, CTFs, or security research.</i>"
    ),
}

# ── Per-action detail text (shown when a slash command is used with no
# arguments) and action prompt (shown after tapping the matching button) ──

DETAIL_TEXTS = {
    "decode": {
        "uz": (
            "📥 <b>Avtomatik dekodlash</b>\n\n"
            "Kodlangan matnni (base64, hex, URL-encoding, binary) avtomatik aniqlab, "
            "zanjirlab ochadi - CyberChef uslubida.\n\n"
            "<b>Foydalanish:</b>\n<code>/decode &lt;matn&gt;</code>\n\n"
            "<b>Misol:</b>\n<code>/decode c2VjdXJpdHkgaXMgaW1wb3J0YW50</code>"
        ),
        "ru": (
            "📥 <b>Автоматическое декодирование</b>\n\n"
            "Автоматически определяет и раскрывает закодированный текст (base64, "
            "hex, URL-encoding, binary) - в стиле CyberChef.\n\n"
            "<b>Использование:</b>\n<code>/decode &lt;текст&gt;</code>\n\n"
            "<b>Пример:</b>\n<code>/decode c2VjdXJpdHkgaXMgaW1wb3J0YW50</code>"
        ),
        "en": (
            "📥 <b>Automatic decoding</b>\n\n"
            "Automatically detects and unwraps encoded text (base64, hex, "
            "URL-encoding, binary) - CyberChef style.\n\n"
            "<b>Usage:</b>\n<code>/decode &lt;text&gt;</code>\n\n"
            "<b>Example:</b>\n<code>/decode c2VjdXJpdHkgaXMgaW1wb3J0YW50</code>"
        ),
    },
    "xor": {
        "uz": (
            "🔑 <b>XOR buzish</b>\n\n"
            "Noma'lum (takrorlanuvchi) kalit bilan XOR qilingan matnni kalitsiz "
            "buzadi. <b>Kiritish hex formatida bo'lishi kerak.</b>\n\n"
            "<b>Foydalanish:</b>\n<code>/xor &lt;hex_shifrmatn&gt;</code>\n\n"
            "<b>Misol:</b>\n<code>/xor 18212a6e3d3c262d27692d3c233e216e2a26376e263c22</code>"
        ),
        "ru": (
            "🔑 <b>Взлом XOR</b>\n\n"
            "Взламывает текст, зашифрованный XOR с неизвестным повторяющимся "
            "ключом, без самого ключа. <b>Ввод должен быть в формате hex.</b>\n\n"
            "<b>Использование:</b>\n<code>/xor &lt;hex-шифртекст&gt;</code>\n\n"
            "<b>Пример:</b>\n<code>/xor 18212a6e3d3c262d27692d3c233e216e2a26376e263c22</code>"
        ),
        "en": (
            "🔑 <b>XOR breaking</b>\n\n"
            "Breaks text XOR-encrypted with an unknown repeating key, without "
            "the key. <b>Input must be in hex format.</b>\n\n"
            "<b>Usage:</b>\n<code>/xor &lt;hex_ciphertext&gt;</code>\n\n"
            "<b>Example:</b>\n<code>/xor 18212a6e3d3c262d27692d3c233e216e2a26376e263c22</code>"
        ),
    },
    "vigenere": {
        "uz": (
            "📜 <b>Vigenère buzish</b>\n\n"
            "Kasiski testi + Index of Coincidence yordamida kalit uzunligini, "
            "so'ng chastota tahlili bilan kalitning o'zini topadi.\n\n"
            "<b>Foydalanish:</b>\n<code>/vigenere &lt;shifrmatn&gt;</code>\n\n"
            "<b>Misol:</b>\n<code>/vigenere EPSUTAHBCGCSNZMCEWUELXVLDBFREKVRDJOPVBVBF</code>"
        ),
        "ru": (
            "📜 <b>Взлом Vigenère</b>\n\n"
            "С помощью теста Касиски и индекса совпадений находит длину ключа, "
            "затем частотным анализом - сам ключ.\n\n"
            "<b>Использование:</b>\n<code>/vigenere &lt;шифртекст&gt;</code>\n\n"
            "<b>Пример:</b>\n<code>/vigenere EPSUTAHBCGCSNZMCEWUELXVLDBFREKVRDJOPVBVBF</code>"
        ),
        "en": (
            "📜 <b>Vigenère breaking</b>\n\n"
            "Uses the Kasiski test + Index of Coincidence to find the key "
            "length, then frequency analysis to recover the key itself.\n\n"
            "<b>Usage:</b>\n<code>/vigenere &lt;ciphertext&gt;</code>\n\n"
            "<b>Example:</b>\n<code>/vigenere EPSUTAHBCGCSNZMCEWUELXVLDBFREKVRDJOPVBVBF</code>"
        ),
    },
    "substitution": {
        "uz": (
            "🔤 <b>Monoalfavit substitution buzish</b>\n\n"
            "Hill-climbing (quadgram statistikasi bilan) orqali harf-almashtirish "
            "jadvalini qayta tiklaydi.\n\n"
            "<b>Foydalanish:</b>\n<code>/substitution &lt;shifrmatn&gt;</code>\n\n"
            "<b>Misol:</b>\n<code>Rth tzdrale ay wlegraoljgte drlhrwthd fjwn rtacdjqid</code>"
        ),
        "ru": (
            "🔤 <b>Взлом моноалфавитной замены</b>\n\n"
            "Восстанавливает таблицу замены букв методом hill-climbing (со "
            "статистикой квадграмм).\n\n"
            "<b>Использование:</b>\n<code>/substitution &lt;шифртекст&gt;</code>\n\n"
            "<b>Пример:</b>\n<code>Rth tzdrale ay wlegraoljgte drlhrwthd fjwn rtacdjqid</code>"
        ),
        "en": (
            "🔤 <b>Monoalphabetic substitution breaking</b>\n\n"
            "Recovers the letter-substitution table via hill-climbing scored "
            "by quadgram statistics.\n\n"
            "<b>Usage:</b>\n<code>/substitution &lt;ciphertext&gt;</code>\n\n"
            "<b>Example:</b>\n<code>Rth tzdrale ay wlegraoljgte drlhrwthd fjwn rtacdjqid</code>"
        ),
    },
    "encrypt": {
        "uz": (
            "✉️ <b>Qurish (shifrlash)</b>\n\n"
            "O'z matningizni shifrlab, keyin botning uni kalitsiz qanday "
            "buzishini sinab ko'ring.\n\n"
            "<code>/caesar 3 hello world</code>\n"
            "<code>/vigenere_encrypt LION the quick brown fox</code>\n"
            "<code>/xor_encrypt LION the quick brown fox</code>\n"
            "<code>/substitution_encrypt &lt;matn&gt;</code>\n\n"
            "<b>Hash / kodlash:</b> <code>/sha256</code>, <code>/sha1</code>, "
            "<code>/md5</code>, <code>/base64_encode &lt;matn&gt;</code>"
        ),
        "ru": (
            "✉️ <b>Шифрование</b>\n\n"
            "Зашифруйте свой текст, а затем посмотрите, как бот взламывает его "
            "без ключа.\n\n"
            "<code>/caesar 3 hello world</code>\n"
            "<code>/vigenere_encrypt LION the quick brown fox</code>\n"
            "<code>/xor_encrypt LION the quick brown fox</code>\n"
            "<code>/substitution_encrypt &lt;текст&gt;</code>\n\n"
            "<b>Hash / кодирование:</b> <code>/sha256</code>, <code>/sha1</code>, "
            "<code>/md5</code>, <code>/base64_encode &lt;текст&gt;</code>"
        ),
        "en": (
            "✉️ <b>Encrypting</b>\n\n"
            "Encrypt your own text, then watch the bot break it without "
            "knowing the key.\n\n"
            "<code>/caesar 3 hello world</code>\n"
            "<code>/vigenere_encrypt LION the quick brown fox</code>\n"
            "<code>/xor_encrypt LION the quick brown fox</code>\n"
            "<code>/substitution_encrypt &lt;text&gt;</code>\n\n"
            "<b>Hash / encoding:</b> <code>/sha256</code>, <code>/sha1</code>, "
            "<code>/md5</code>, <code>/base64_encode &lt;text&gt;</code>"
        ),
    },
    "affine": {
        "uz": (
            "🔢 <b>Affine shifrini buzish</b>\n\n"
            "E(x) = (a·x + b) mod 26 - barcha 312 ta mumkin bo'lgan (a, b) "
            "juftligini sinab, chi-squared tahlili bilan eng mosini topadi.\n\n"
            "<b>Foydalanish:</b>\n<code>/affine &lt;shifrmatn&gt;</code>"
        ),
        "ru": (
            "🔢 <b>Взлом Affine</b>\n\n"
            "E(x) = (a·x + b) mod 26 - перебирает все 312 пар (a, b) и "
            "выбирает лучшую по хи-квадрат анализу.\n\n"
            "<b>Использование:</b>\n<code>/affine &lt;шифртекст&gt;</code>"
        ),
        "en": (
            "🔢 <b>Affine cipher breaking</b>\n\n"
            "E(x) = (a·x + b) mod 26 - tries all 312 valid (a, b) pairs and "
            "picks the best fit via chi-squared analysis.\n\n"
            "<b>Usage:</b>\n<code>/affine &lt;ciphertext&gt;</code>"
        ),
    },
    "affine_encrypt": {
        "uz": (
            "🔢 <b>Affine bilan shifrlash</b>\n\n"
            "<code>a b matn</code> formatida yuboring (a - 26 bilan o'zaro tub "
            "son: 1,3,5,7,9,11,15,17,19,21,23,25).\nMisol: "
            "<code>5 8 hello world</code> 👇"
        ),
        "ru": (
            "🔢 <b>Шифрование Affine</b>\n\n"
            "Отправьте в формате <code>a b текст</code> (a - взаимно просто с "
            "26: 1,3,5,7,9,11,15,17,19,21,23,25).\nПример: "
            "<code>5 8 hello world</code> 👇"
        ),
        "en": (
            "🔢 <b>Affine encryption</b>\n\n"
            "Send as <code>a b text</code> (a must be coprime with 26: "
            "1,3,5,7,9,11,15,17,19,21,23,25).\nExample: "
            "<code>5 8 hello world</code> 👇"
        ),
    },
    "rot13": {
        "uz": "🔄 <b>ROT13</b>\n\nMatningizni yuboring 👇",
        "ru": "🔄 <b>ROT13</b>\n\nОтправьте ваш текст 👇",
        "en": "🔄 <b>ROT13</b>\n\nSend your text 👇",
    },
    "rot47": {
        "uz": "🔄 <b>ROT47</b>\n\nMatningizni yuboring 👇",
        "ru": "🔄 <b>ROT47</b>\n\nОтправьте ваш текст 👇",
        "en": "🔄 <b>ROT47</b>\n\nSend your text 👇",
    },
    "analyze": {
        "uz": "📊 <b>Statistik tahlil</b>\n\nTahlil qilinadigan matnni yuboring 👇",
        "ru": "📊 <b>Статистический анализ</b>\n\nОтправьте текст для анализа 👇",
        "en": "📊 <b>Statistical analysis</b>\n\nSend the text to analyze 👇",
    },
    "personal_wordlist": {
        "uz": (
            "🎯 <b>Shaxsiy wordlist generatori</b>\n\n"
            "<code>/personal_wordlist &lt;ism, taxallus, yil, ...&gt;</code>\n"
            "Misol: <code>/personal_wordlist John, Smith, 1995</code>\n\n"
            "⚠️ <i>Faqat o'zingiz yoki ruxsat bergan shaxs ma'lumotlaridan "
            "foydalaning.</i>"
        ),
        "ru": (
            "🎯 <b>Генератор личного wordlist</b>\n\n"
            "<code>/personal_wordlist &lt;имя, прозвище, год, ...&gt;</code>\n"
            "Пример: <code>/personal_wordlist John, Smith, 1995</code>\n\n"
            "⚠️ <i>Используйте только свои данные или данные с разрешения "
            "владельца.</i>"
        ),
        "en": (
            "🎯 <b>Personal wordlist generator</b>\n\n"
            "<code>/personal_wordlist &lt;name, nickname, year, ...&gt;</code>\n"
            "Example: <code>/personal_wordlist John, Smith, 1995</code>\n\n"
            "⚠️ <i>Only use your own data, or data from someone who gave "
            "permission.</i>"
        ),
    },
    "sha256": {
        "uz": "#️⃣ <b>SHA-256 hash</b>\n\nMatningizni yuboring 👇",
        "ru": "#️⃣ <b>SHA-256 hash</b>\n\nОтправьте ваш текст 👇",
        "en": "#️⃣ <b>SHA-256 hash</b>\n\nSend your text 👇",
    },
    "sha1": {
        "uz": "#️⃣ <b>SHA-1 hash</b>\n\nMatningizni yuboring 👇",
        "ru": "#️⃣ <b>SHA-1 hash</b>\n\nОтправьте ваш текст 👇",
        "en": "#️⃣ <b>SHA-1 hash</b>\n\nSend your text 👇",
    },
    "md5": {
        "uz": "#️⃣ <b>MD5 hash</b>\n\nMatningizni yuboring 👇",
        "ru": "#️⃣ <b>MD5 hash</b>\n\nОтправьте ваш текст 👇",
        "en": "#️⃣ <b>MD5 hash</b>\n\nSend your text 👇",
    },
    "base64_encode": {
        "uz": "🔡 <b>Base64 kodlash</b>\n\nMatningizni yuboring 👇",
        "ru": "🔡 <b>Кодирование Base64</b>\n\nОтправьте ваш текст 👇",
        "en": "🔡 <b>Base64 encoding</b>\n\nSend your text 👇",
    },
    "caesar": {
        "uz": (
            "🅰️ <b>Caesar shifrlash</b>\n\n<code>shift matn</code> formatida "
            "yuboring.\nMisol: <code>3 hello world</code> 👇"
        ),
        "ru": (
            "🅰️ <b>Шифрование Caesar</b>\n\nОтправьте в формате "
            "<code>сдвиг текст</code>.\nПример: <code>3 hello world</code> 👇"
        ),
        "en": (
            "🅰️ <b>Caesar encryption</b>\n\nSend as <code>shift text</code>.\n"
            "Example: <code>3 hello world</code> 👇"
        ),
    },
    "vigenere_encrypt": {
        "uz": (
            "📜 <b>Vigenère bilan shifrlash</b>\n\n<code>kalit matn</code> "
            "formatida yuboring.\nMisol: <code>LION the quick brown fox</code> 👇"
        ),
        "ru": (
            "📜 <b>Шифрование Vigenère</b>\n\nОтправьте в формате "
            "<code>ключ текст</code>.\nПример: "
            "<code>LION the quick brown fox</code> 👇"
        ),
        "en": (
            "📜 <b>Vigenère encryption</b>\n\nSend as <code>key text</code>.\n"
            "Example: <code>LION the quick brown fox</code> 👇"
        ),
    },
    "xor_encrypt": {
        "uz": (
            "🔑 <b>XOR bilan shifrlash</b>\n\n<code>kalit matn</code> formatida "
            "yuboring.\nMisol: <code>LION the quick brown fox</code> 👇"
        ),
        "ru": (
            "🔑 <b>Шифрование XOR</b>\n\nОтправьте в формате "
            "<code>ключ текст</code>.\nПример: "
            "<code>LION the quick brown fox</code> 👇"
        ),
        "en": (
            "🔑 <b>XOR encryption</b>\n\nSend as <code>key text</code>.\n"
            "Example: <code>LION the quick brown fox</code> 👇"
        ),
    },
    "substitution_encrypt": {
        "uz": "🔤 <b>Tasodifiy substitution bilan shifrlash</b>\n\nMatningizni yuboring 👇",
        "ru": "🔤 <b>Шифрование случайной заменой</b>\n\nОтправьте ваш текст 👇",
        "en": "🔤 <b>Random substitution encryption</b>\n\nSend your text 👇",
    },
}

ACTION_PROMPTS = {
    "decode": {
        "uz": "📥 <b>Avtomatik dekodlash</b>\n\nKodlangan matningizni yuboring 👇",
        "ru": "📥 <b>Автоматическое декодирование</b>\n\nОтправьте закодированный текст 👇",
        "en": "📥 <b>Automatic decoding</b>\n\nSend your encoded text 👇",
    },
    "xor": {
        "uz": (
            "🔑 <b>XOR buzish</b>\n\nShifrmatnni <b>hex</b> formatida yuboring "
            "(masalan: <code>1a2b3c...</code>) 👇"
        ),
        "ru": (
            "🔑 <b>Взлом XOR</b>\n\nОтправьте шифртекст в формате <b>hex</b> "
            "(например: <code>1a2b3c...</code>) 👇"
        ),
        "en": (
            "🔑 <b>XOR breaking</b>\n\nSend the ciphertext in <b>hex</b> format "
            "(e.g. <code>1a2b3c...</code>) 👇"
        ),
    },
    "vigenere": {
        "uz": "📜 <b>Vigenère buzish</b>\n\nShifrmatningizni yuboring 👇",
        "ru": "📜 <b>Взлом Vigenère</b>\n\nОтправьте ваш шифртекст 👇",
        "en": "📜 <b>Vigenère breaking</b>\n\nSend your ciphertext 👇",
    },
    "substitution": {
        "uz": "🔤 <b>Substitution buzish</b>\n\nShifrmatningizni yuboring 👇",
        "ru": "🔤 <b>Взлом замены</b>\n\nОтправьте ваш шифртекст 👇",
        "en": "🔤 <b>Substitution breaking</b>\n\nSend your ciphertext 👇",
    },
    "caesar": DETAIL_TEXTS["caesar"],
    "vigenere_encrypt": DETAIL_TEXTS["vigenere_encrypt"],
    "xor_encrypt": DETAIL_TEXTS["xor_encrypt"],
    "substitution_encrypt": DETAIL_TEXTS["substitution_encrypt"],
    "sha256": DETAIL_TEXTS["sha256"],
    "sha1": DETAIL_TEXTS["sha1"],
    "md5": DETAIL_TEXTS["md5"],
    "base64_encode": DETAIL_TEXTS["base64_encode"],
    "affine": {
        "uz": "🔢 <b>Affine buzish</b>\n\nShifrmatningizni yuboring 👇",
        "ru": "🔢 <b>Взлом Affine</b>\n\nОтправьте ваш шифртекст 👇",
        "en": "🔢 <b>Affine breaking</b>\n\nSend your ciphertext 👇",
    },
    "affine_encrypt": DETAIL_TEXTS["affine_encrypt"],
    "rot13": DETAIL_TEXTS["rot13"],
    "rot47": DETAIL_TEXTS["rot47"],
    "analyze": DETAIL_TEXTS["analyze"],
    # Note: "personal_wordlist" has no entry here on purpose — its button
    # flow is a multi-step form (see PersonalWordlistForm in handlers.py)
    # special-cased before this table is ever consulted; only its
    # DETAIL_TEXTS entry (shown for /personal_wordlist with no args) is used.
}

WORDLIST_DESCRIPTIONS = {
    "wl_top10k": {
        "uz": "Eng ko'p ishlatiladigan 10 000 parol - tezkor CTF uchun",
        "ru": "10 000 самых часто используемых паролей - для быстрого CTF",
        "en": "The 10,000 most commonly used passwords - for quick CTF use",
    },
    "wl_ncsc100k": {
        "uz": "Buyuk Britaniya NCSC rasmiy nashr etgan 100 000 eng zaif parol",
        "ru": "100 000 самых слабых паролей, официально опубликованных NCSC (Великобритания)",
        "en": "100,000 weakest passwords, officially published by the UK's NCSC",
    },
    "wl_pwdb1m": {
        "uz": "Pwdb loyihasining 1 million eng ko'p uchraydigan paroli",
        "ru": "1 миллион самых распространённых паролей из проекта Pwdb",
        "en": "1 million most common passwords from the Pwdb project",
    },
    "wl_worst500": {
        "uz": "Tarixdagi eng ko'p tanqid qilingan 500 ta zaif parol",
        "ru": "500 самых критикуемых слабых паролей в истории",
        "en": "The 500 most notoriously weak passwords in history",
    },
    "wl_top10m": {
        "uz": "xato.net'ning to'liq 10 milliondan iborat parollar bazasi",
        "ru": "Полная база из 10 миллионов паролей от xato.net",
        "en": "xato.net's full database of 10 million passwords",
    },
}


def t(lang: str, table: dict, key: str | None = None) -> str:
    """Look up a translation. If `table` is itself a per-language dict
    (no `key`), looks lang up directly; otherwise table[key][lang]."""
    if key is not None:
        table = table[key]
    return table.get(lang, table.get(DEFAULT_LANGUAGE, ""))


def label(lang: str, key: str) -> str:
    return LABELS[key].get(lang, LABELS[key][DEFAULT_LANGUAGE])
