# DecodeWizard — Cryptanalysis Bot

Telegram bot: noma'lum kalit bilan shifrlangan matnni **o'z algoritmlari bilan
buzadi** (tashqi `ciphey`/`pycipher` kabi kutubxonalarsiz), kodlangan matnni
avtomatik aniqlab ochadi, shifrlaydi, hash hisoblaydi va parol/wordlist
generatsiya qiladi. **3 tilni** (o'zbek, rus, ingliz) to'liq qo'llab-quvvatlaydi.

**Muallif:** Muhammad Sayid Qosimov · Loyiha #3 (Capstone)

Arxitektura va tahdid modeli: [docs/DESIGN.md](docs/DESIGN.md), [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## Bot nima qiladi

| Bo'lim | Buyruqlar | Tavsif |
|---|---|---|
| 🔓 **Buzish** | `/xor` `/vigenere` `/substitution` `/affine` | Kalit berilmasa ham klassik shifrlarni statistik tahlil orqali buzadi |
| 🔍 **Avtomatik aniqlash** | `/decode` | Base64/Hex/URL/binary zanjirini aniqlab ochadi (CyberChef uslubi) |
| ✉️ **Shifrlash** | `/caesar` `/vigenere_encrypt` `/xor_encrypt` `/substitution_encrypt` `/affine_encrypt` `/rot13` `/rot47` | O'z matningizni shifrlab, keyin botning uni qanday buzishini sinab ko'rasiz |
| #️⃣ **Hash/kodlash** | `/sha256` `/sha1` `/md5` `/base64_encode` | Standart kriptografik primitivlar |
| 📊 **Tahlil** | `/analyze` | Entropiya, Index of Coincidence, chi-squared, harf chastotasi |
| 📁 **Wordlist** | `/wordlists` `/personal_wordlist` | Tayyor parol ro'yxatlari (SecLists) + shaxsiy ma'lumotlardan generatsiya |
| 🔑 **Generatorlar** | `/genpass` `/randkey` | Kuchli parol / tasodifiy kriptografik kalit |
| 🕐 **Boshqa** | `/history` `/language` `/help` | So'rovlar tarixi, til tanlash, yordam |

Barcha funksiyalar **tugma orqali ham** ishlaydi — `/start` yuboring, tugmani
bosing, so'ng matningizni oddiy xabar sifatida yuboring (buyruq yozish shart
emas). Natijalarda qo'shimcha **Mini App** (vizual zanjir + harf-chastota
grafigi) ham bor.

## Mahalliy ishga tushirish

### 1. Bog'liqliklarni o'rnatish

```bash
pip install -e .[dev]
```

### 2. `.env` faylini tayyorlash

```bash
cp .env.example .env
```

`.env` ichida to'ldiring:
- `BOT_TOKEN` — [@BotFather](https://t.me/BotFather)dan oling
- `WEBHOOK_SECRET_TOKEN` — tasodifiy qiymat: `python -c "import secrets; print(secrets.token_hex(32))"`
- `WEBHOOK_BASE_URL` — pastga qarang (devtunnel manzili)
- `ADMIN_USER_IDS` — o'z Telegram user ID'ingiz ([@userinfobot](https://t.me/userinfobot)dan oling)

### 3. Webhook uchun tunnel (HTTPS talab qilinadi, polling yo'q)

Doimiy manzil olish uchun — bir martalik sozlash:

```bash
devtunnel create cryptobot --allow-anonymous
devtunnel port create cryptobot -p 8080
```

Har safar kompyuterni yoqqandan keyin — shu ikki qadam:

**1-terminal:**
```bash
devtunnel host cryptobot
```

Chiqqan manzilni (masalan `https://xxxxx-8080.eun1.devtunnels.ms`) `.env`
faylidagi `WEBHOOK_BASE_URL`ga qo'ying (**faqat birinchi marta** — keyin bu
manzil doimiy qoladi).

**2-terminal:**
```bash
python -m app.bot.main
```

Loglarda `webhook set to https://...` chiqishi kerak — bot tayyor.

> ⚠️ **Bitta nusxani ishga tushiring.** Ikkinchi marta ishga tushirsangiz,
> `main.py` portni band ko'rib, aniq xato bilan to'xtaydi (webhook'ni
> buzmaydi) — ikkinchi nusxani boshlamang, avval birinchisini to'xtating.

### Testlar va kod sifati

```bash
pytest -v
bandit -r app -ll
ruff check app tests
```

## Docker bilan ishga tushirish (ixtiyoriy, production uchun)

Loyiha Docker Compose orqali ham ishga tushadi (baseline-10 talabi uchun
tayyor, lekin kundalik mahalliy ishlatish uchun shart emas):

```bash
docker compose build bot   # Dockerfile to'g'ri ishlashini tekshiradi
docker compose up --build  # to'liq (nginx + bot), deploy/certs/ ichida TLS kerak
```

## Xavfsizlik bazasi (qisqacha)

Barcha 13 majburiy band `docs/THREAT_MODEL.md`da batafsil yoritilgan: `.env`
sirlari git tarixidan tashqarida, admin faqat Telegram user ID bo'yicha,
parametrlashtirilgan SQL, `eval`/`exec`/`shell=True` yo'q, har bir
cryptanalysis job alohida izolyatsiya qilingan subprocessda CPU/vaqt/xotira
limiti bilan ishlaydi (`app/worker/run_job.py`), webhook `secret_token` bilan
tasdiqlanadi, shaxsiy wordlist generatori kiritilgan ma'lumotni bazaga
saqlamaydi.

## Loyiha tuzilishi

```
app/
  core/        — sof Python cryptanalysis "engine" (Telegram'dan mustaqil, test qilingan)
  worker/      — izolyatsiyalangan subprocess runner (CPU/vaqt/xotira limiti)
  bot/         — aiogram 3 webhook handlerlar, i18n, DB, rate-limit, admin
    i18n.py        — barcha matnlar (uz/ru/en)
    handlers.py    — buyruqlar va tugma oqimlari
    formatting.py  — xabar shablonlari
    keyboards.py   — inline tugmalar
    webapp/        — Mini App (vizual decode natijasi)
docs/          — design doc, threat model
deploy/        — nginx config, TLS sertifikatlar (gitignored)
scripts/       — quadgram statistikasini qurish skripti
tests/         — pytest (52 test)
```
