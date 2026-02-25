# 🤖 CV Bot — Europa Pass Style

**PDF + DOCX** formatida professional CV tayyorlaydigan Telegram bot.  
Tillar: 🇺🇿 O'zbek | 🇷🇺 Русский | 🇬🇧 English

---

## 📁 Fayl tuzilmasi

```
cv_bot/
├── bot.py             # Asosiy bot
├── cv_generator.py    # PDF + DOCX generator
├── requirements.txt   # Kutubxonalar
├── Procfile           # Railway uchun
├── railway.toml       # Railway config
├── runtime.txt        # Python versiyasi
├── .env.example       # Token namunasi (local uchun)
├── .gitignore         # Git ignore
└── README.md
```

---

## 🚀 Railway da Deploy qilish

### 1️⃣ BotFather dan token oling
1. Telegram da [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` yuboring → nom va username bering
3. Tokenni nusxalab oling: `7123456789:AAFxxx...`

### 2️⃣ GitHub ga yuklang
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/SIZNING/cv-bot.git
git push -u origin main
```

### 3️⃣ Railway da sozlang
1. [railway.app](https://railway.app) ga kiring
2. **New Project** → **Deploy from GitHub repo**
3. Repozitoriyangizni tanlang
4. **Variables** bo'limiga o'ting:
   ```
   BOT_TOKEN = 7123456789:AAFxxxxxxxxxxxxxxxx
   ```
5. Deploy avtomatik boshlanadi ✅

### 4️⃣ Tekshirish
Railway **Logs** bo'limida:
```
✅ Bot ishga tushdi!
```
ko'rsangiz — bot ishlayapti!

---

## 💻 Local ishga tushirish (test uchun)

```bash
# 1. Klonlash
git clone https://github.com/SIZNING/cv-bot.git
cd cv-bot

# 2. Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Kutubxonalar
pip install -r requirements.txt

# 4. Token sozlash
cp .env.example .env
# .env faylni oching va tokenni qo'ying

# 5. Ishga tushirish
python bot.py
```

---

## 🎨 Bot imkoniyatlari

| Xususiyat | Tavsif |
|-----------|--------|
| 🌐 3 til | O'zbek, Rus, Ingliz |
| 📸 Foto | Profil rasmi yuklash |
| 📄 PDF | Europa Pass dizayni (ko'k sidebar + oltin detallar) |
| 📝 DOCX | Microsoft Word formati |
| 🗣 Tillar | CEFR darajalari (A1-C2) |
| 🛠 Ko'nikmalar | Kategoriyalangan |
| 🏆 Sertifikatlar | Optional |

---

## 📋 Bot qadamlari

```
/start → Til → Rasm → Shaxsiy ma'lumot → Kontakt
→ Ijtimoiy → Maqsad → Ta'lim → Tajriba
→ Ko'nikmalar → Tillar → Sertifikatlar → Qiziqishlar
→ Format (PDF/DOCX/Ikkalasi) → Tasdiqlash → 📄 CV!
```

**Buyruqlar:**
- `/start` — Boshlash / qayta boshlash
- `/skip` — Ixtiyoriy maydonni o'tkazish
- `/done` — Ro'yxatni tugatish
- `/cancel` — Bekor qilish
