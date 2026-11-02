# Design Doc — Cryptanalysis Bot

**Muallif:** Muhammad Sayid Qosimov
**Loyiha:** #3 — Cryptanalysis bot (Capstone, individual)
**Sana:** 2026-11-02 (hafta 1)

## 1. Maqsad

Telegram orqali ishlaydigan bot:

1. Kiritilgan matnni (shifrmatn yoki kodlangan satr) **avtomatik tanib**, zanjirli dekodlash amallarini (base64 → hex → XOR → URL-decode va h.k.) qo'llab, o'qiladigan natijaga olib keladi (CyberChef uslubi).
2. Klassik shifrlarni **o'z kuchi bilan buzadi** (tashqi `ciphey` kabi kutubxonasiz):
   - Vigenère — Kasiski testi + Index of Coincidence (IoC)
   - Monoalfavit o'rin almashtirish — hill-climbing + quadgram scoring
   - Takrorlanuvchi kalitli XOR — kalit uzunligini aniqlash + har bir ustunni single-byte XOR bilan buzish

Botning o'zi ham xavfsizlik talablariga javob berishi shart (CTF/pentest material emas, lekin "cryptanalysis oracle" sifatida suiiste'mol qilinmasligi kerak).

## 2. Komponentlar (arxitektura)

```
                    HTTPS (webhook, secret_token tekshiriladi)
Telegram API  ──────────────────────────────────────▶  nginx (TLS termination)
                                                            │
                                                            ▼
                                                    bot-service (aiogram 3)
                                                      - input validatsiya
                                                      - rate limiting (per user_id)
                                                      - admin allowlist (user ID)
                                                            │
                                                job yaratadi, navbatga qo'yadi
                                                            ▼
                                                    Redis queue (job navbati)
                                                            │
                                                            ▼
                                            worker-service (ishonchsiz kodni alohida konteynerda bajaradi)
                                              - CPU/vaqt/xotira limiti (resource.setrlimit + Docker limits)
                                              - core engine (detector, chain, breakers) shu yerda ishlaydi
                                              - bot-service bilan umumiy kod yo'q, faqat umumiy "core" paket
                                                            │
                                                            ▼
                                                 natija → Postgres/SQLite (shifrlangan maydonlar)
                                                            │
                                                            ▼
                                             bot-service natijani foydalanuvchiga yuboradi
```

**Konteynerlar (docker-compose):**
| Servis | Vazifa | Imtiyoz |
|---|---|---|
| `nginx` | TLS termination, webhook endpoint | non-root |
| `bot` | aiogram 3, webhook handler, validatsiya, rate-limit, job'larni ishga tushiradi | non-root, read-only FS |
| `db` | SQLite (dev) / Postgres (prod) — foydalanuvchi tarixi, audit log | non-root |

**Worker izolyatsiyasi (MVP, v1):** har bir cryptanalysis job (`app/worker/run_job.py`) `bot` konteyneri ichida **alohida OS processi** sifatida ishga tushiriladi (`asyncio.create_subprocess_exec`), umumiy kod/holat ulashilmaydi:

- Subprocess ichida `resource.setrlimit` orqali CPU vaqti (`RLIMIT_CPU`) va xotira (`RLIMIT_AS`) cheklanadi (Linux konteynerda; Windows'da dev paytida bu limit o'tkazib yuboriladi, faqat wall-clock timeout ishlaydi).
- Bot tomonida `asyncio.wait_for(..., timeout=JOB_TIMEOUT_SECONDS)` — qo'shimcha xavfsizlik qatlami, subprocess javob bermasa `kill()` qilinadi.
- Subprocessga kirish/chiqish faqat JSON orqali (stdin/stdout) — `eval`/`exec` yo'q, `shell=True` yo'q.

*Keyingi bosqich (v2, vaqt imkon bersa):* bu subprocess modelini alohida `worker` konteyneriga va Redis job-navbatiga ko'chirish — arxitektura shunga tayyor (job interfeysi allaqachon "input JSON → output JSON" shaklida ajratilgan), lekin 2 kunlik MVP doirasida process-darajasidagi izolyatsiya baseline-12 talabini (CPU/vaqt/xotira limiti, ishonchsiz kod alohida) qondiradi.

## 3. Core engine (sof Python, Telegram'dan mustaqil)

`app/core/` — hech qanday tashqi cryptanalysis kutubxonasi ishlatilmaydi.

- `detector.py` — Shannon entropy, belgilar to'plami (base64/hex/URL regex) asosida kodlash turini aniqlash, har biriga ishonch (%) bali.
- `chain.py` — aniqlangan kodlashlarni ketma-ket qo'llab, "chain" quradi; max chuqurlik va cycle-detection bilan cheksiz tsikldan himoyalanadi.
- `scoring.py` — ingliz tili uchun monogram/bigram/quadgram log-ehtimollik jadvali (`app/core/data/quadgrams.json`, mahalliy korpusdan qurilgan).
- `xor_breaker.py` — repeating-key XOR: kalit uzunligini (Hamming distance / normalized) topish → har ustunni single-byte XOR + chastota skoring bilan buzish.
- `vigenere_breaker.py` — Kasiski testi (takrorlanuvchi n-gramlar orasidagi masofalarning GCD'i) + IoC bilan tasdiqlash → har ustun uchun chi-squared chastota tahlili → kalitni qayta tiklash.
- `substitution_breaker.py` — hill-climbing (random restart + simulated annealing elementi): ikkita harfni almashtirib ko'rish, quadgram skori yaxshilansa qabul qilish.
- Har bir funksiya **CPU/vaqt limiti bilan** chaqiriladi (worker darajasida `signal.alarm` / jarayon timeout orqali, Linux konteynerda).

## 4. Ma'lumotlar bazasi

- `users` — telegram_id, til, ro'yxatdan o'tgan vaqt
- `jobs` — job_id, user_id, holat, boshlanish/tugash vaqti, natija (shifrlangan maydon)
- `admin_audit_log` — admin_id, amal, vaqt, (append-only, imzolangan hash-chain — manipulatsiyani aniqlash uchun)

Shifrmatn/natija **maksimal N kun** saqlanadi, keyin avtomatik o'chiriladi (data minimization, baseline-7).

## 5. "Eng qiyin qism" — qanday hal qilinadi

1. **O'z algoritmlarim**: `ciphey`/`pycipher` kabi kutubxonalar ishlatilmaydi — barcha buzish mantiqi `app/core/`da, unit testlar bilan tasdiqlangan.
2. **CPU/vaqt limiti**: har bir job alohida worker jarayonida, `multiprocessing` + timeout orqali bajariladi; timeout'dan oshsa job "failed: timeout" deb belgilanadi, resurs tortib olinmaydi.

## 6. Texnologiyalar

Python 3.12, aiogram 3, Redis, PostgreSQL/SQLite, Docker Compose, pytest, bandit, semgrep, gitleaks, pip-audit (CI'da).

## 7. Keyingi hujjat

Tahdidlar va ularga qarshi choralar — [THREAT_MODEL.md](THREAT_MODEL.md).
