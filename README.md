# Cryptanalysis Bot

Telegram bot: avtomatik kodlash zanjirini (base64/hex/url/binary) aniqlab ochadi
va klassik shifrlarni (Vigenère, monoalfavit substitution, repeating-key XOR)
o'z algoritmlari bilan buzadi — tashqi `ciphey`/`pycipher` kabi kutubxonalarsiz.

**Muallif:** Muhammad Sayid Qosimov · Loyiha #3 (Capstone)

Arxitektura va tahdid modeli: [docs/DESIGN.md](docs/DESIGN.md), [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## Buyruqlar

| Buyruq | Tavsif |
|---|---|
| `/decode <matn>` | Zanjirli avtomatik dekodlash (CyberChef uslubi) |
| `/xor <hex>` | Takrorlanuvchi kalitli XOR'ni buzadi (kiritish **hex** formatida) |
| `/vigenere <matn>` | Vigenère shifrini Kasiski testi + IoC bilan buzadi |
| `/substitution <matn>` | Monoalfavit substitutsiyani hill-climbing bilan buzadi |
| `/stats` | (admin) eski job yozuvlarini tozalaydi |
| `/auditlog` | (admin) audit log hash-zanjirining yaxlitligini tekshiradi |

## Mahalliy ishga tushirish (testlar, kod sifatini tekshirish)

```bash
pip install -e .[dev]
pytest -v
bandit -r app -ll
ruff check app tests
```

## Docker bilan ishga tushirish (demo)

1. O'z botingizni [@BotFather](https://t.me/BotFather) orqali yarating, tokenni oling.
2. `.env` faylini tayyorlang:

```bash
cp .env.example .env
```

`.env` ichida `BOT_TOKEN`, `WEBHOOK_SECRET_TOKEN` (tasodifiy 32 bayt hex),
`WEBHOOK_BASE_URL` (tashqi HTTPS manzil) va `ADMIN_USER_IDS` (o'z Telegram
user ID'ingiz) to'ldiring.

3. Webhook HTTPS talab qiladi. Mahalliy demo uchun eng tez yo'l — `ngrok` orqali
   tunnel ochish (baseline "webhook over HTTPS, no polling" talabini saqlab
   qolamiz, faqat sertifikatni ngrok beradi):

```bash
ngrok http 8080
```

   Keyin `.env`'dagi `WEBHOOK_BASE_URL`'ni ngrok bergan `https://...ngrok-free.app`
   manziliga qo'ying va to'g'ridan-to'g'ri botni ishga tushiring (nginx'siz,
   dev rejimida):

```bash
pip install -e .
python -m app.bot.main
```

4. **Haqiqiy production** uchun (o'z domeningiz + TLS bilan) `docker-compose.yml`
   ishlatiladi — `deploy/certs/` ichiga `fullchain.pem` va `privkey.pem`
   qo'ying (Let's Encrypt yoki o'z-o'ziga imzolangan), so'ng:

```bash
docker compose up --build
```

## Xavfsizlik bazasi (qisqacha)

Barcha 13 majburiy band `docs/THREAT_MODEL.md`da batafsil yoritilgan: `.env`
sirlari git tarixidan tashqarida, admin faqat Telegram user ID bo'yicha,
parametrlashtirilgan SQL, `eval`/`exec`/`shell=True` yo'q, har bir
cryptanalysis job alohida izolyatsiya qilingan subprocessda CPU/vaqt/xotira
limiti bilan ishlaydi (`app/worker/run_job.py`), webhook `secret_token` bilan
tasdiqlanadi, konteynerlar non-root + read-only FS.

## Loyiha tuzilishi

```
app/
  core/        — sof Python cryptanalysis "engine" (Telegram'dan mustaqil, test qilingan)
  worker/      — izolyatsiyalangan subprocess runner (CPU/vaqt/xotira limiti)
  bot/         — aiogram 3 webhook handlerlar, DB, rate-limit, admin
docs/          — design doc, threat model
deploy/        — nginx config, TLS sertifikatlar (gitignored)
tests/         — pytest (core: 15 test, bot: 3 test)
```
