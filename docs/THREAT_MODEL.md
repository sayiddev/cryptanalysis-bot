# Threat Model — Cryptanalysis Bot

**Muallif:** Muhammad Sayid Qosimov · **Sana:** 2026-11-02

Metodologiya: STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) komponent bo'yicha qo'llanildi.

| # | Tahdid | STRIDE | Jiddiylik | Mitigatsiya |
|---|---|---|---|---|
| 1 | Bot token/API kaliti git tarixiga yoki logga tushib qolishi | Information Disclosure | Critical | `.env` + `.gitignore`; CI'da `gitleaks` har commit'ni skanerlaydi; loglarda token hech qachon chop etilmaydi |
| 2 | Soxta webhook so'rovi (Telegram emas, hujumchi yuborgan) | Spoofing | High | `X-Telegram-Bot-Api-Secret-Token` header har so'rovda tekshiriladi; mos kelmasa 403 |
| 3 | Katta/maxsus tuzilgan input bilan DoS (masalan, 10 MB matn yoki chuqur rekursiv chain) | Denial of Service | High | Input uzunligi/hajmi oldindan tekshiriladi; chain'da max chuqurlik + cycle detection |
| 4 | Hill-climbing/Kasiski kabi CPU-talab operatsiyalar resursni band qilib qo'yishi (bitta foydalanuvchi butun botni to'xtatadi) | Denial of Service | High | Har bir job alohida worker konteynerida, CPU/vaqt/xotira limiti bilan (timeout → job bekor qilinadi) |
| 5 | SQL in'eksiya (foydalanuvchi matni DB so'roviga qo'shilsa) | Tampering | High | Faqat parametrlashtirilgan so'rovlar (ORM yoki `?` placeholder); foydalanuvchi matni hech qachon so'rov matniga concat qilinmaydi |
| 6 | Admin buyruqlariga ruxsatsiz kirish (username almashtirib soxtalashtirish) | Elevation of Privilege | Critical | Admin tekshiruvi faqat Telegram **user ID** allowlist orqali, username emas |
| 7 | Flood/spam — bitta foydalanuvchi minglab so'rov yuboradi | Denial of Service | Medium | Per-user rate limiting (token bucket, masalan 10 so'rov/daqiqa) |
| 8 | Boshqa birovning maxfiy ma'lumotini (masalan, kompaniyadan o'g'irlangan shifrlangan ma'lumot) bot orqali ochish — bot "deshifrlash oracle" sifatida suiiste'mol qilinishi | Information Disclosure | Medium | Foydalanish shartlari (bot ichida ko'rsatiladi); audit log (kim nima yuborgani, vaqt bilan); faqat zaif/klassik shifrlarga yo'naltirilgan — zamonaviy AES kabi kuchli shifrlarni buzish imkoni yo'q |
| 9 | Xato xabarlarida ichki stack trace/fayl yo'llari oshkor bo'lishi | Information Disclosure | Low | Foydalanuvchiga faqat umumiy xabar ("Xatolik yuz berdi"); to'liq detal faqat server logiga |
| 10 | Dependency supply-chain hujumi (zararli PyPI paketi) | Tampering | Medium | `pip-audit` CI'da; versiyalar pinned (`requirements.txt` hash bilan) |
| 11 | Konteyner ichida imtiyozni oshirish (root sifatida ishlash, worker qochib chiqishi) | Elevation of Privilege | High | Barcha konteynerlar non-root user; read-only filesystem; worker tarmoqsiz (`network_mode: none`) |
| 12 | Foydalanuvchi tarixi/natijalari bazada cheksiz saqlanib, keyin sizib chiqishi | Information Disclosure | Medium | Data minimization — natijalar N kundan keyin avtomatik o'chiriladi; nozik maydonlar shifrlangan holda saqlanadi |
| 13 | Admin amallarini inkor etish (kim banni olib tashlagani noma'lum) | Repudiation | Medium | Append-only audit log, har bir admin amali imzolanadi (hash-chain), vaqt belgisi bilan |
| 14 | Takroriy webhook update'lari (Telegram qayta yuborishi) natijada ikki marta bajarilgan job | Tampering | Low | `update_id` asosida idempotentlik — bir xil update ikki marta qayta ishlanmaydi |
| 15 | CI/CD pipeline orqali zararli kod kiritish (masalan, PR orqali) | Tampering | Medium | CI'da bandit/semgrep statik tahlil; branch protection; o'z repo, faqat o'zim push qilaman |

## Qo'shimcha eslatma

Loyihaning tabiati bo'yicha bot "attack tool" emas — faqat **klassik va zaif** shifrlash usullarini (Vigenère, monoalfavit, repeating-key XOR) buzadi. Zamonaviy shifrlarni (AES, RSA to'g'ri parametrlar bilan) buzish imkoniyati yo'q va bu botning doirasidan tashqarida — shuning uchun "universal deshifrlash vositasi" sifatida suiiste'mol qilish xavfi cheklangan, lekin 8-band baribir audit log bilan yumshatiladi.
