# 🤖 CV Bot - Europa Pass Style
## O'zbek | Русский | English

Xalqaro Europa Pass uslubida **PDF + DOCX** formatida professional CV tayyorlaydigan Telegram bot.

---

## 📁 Fayl tuzilmasi

```
cv_bot/
├── bot.py            # Asosiy bot fayli
├── cv_generator.py   # PDF va DOCX generator
├── requirements.txt  # Kutubxonalar
└── README.md         # Ushbu fayl
```

---

## ⚡ O'rnatish va ishga tushirish

### 1. Bot tokeni olish
1. Telegramda [@BotFather](https://t.me/BotFather) ga boring
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: `MyCVBot`)
4. Username kiriting (masalan: `my_cv_creator_bot`)
5. Token olasiz: `7123456789:AAF...xyz`

### 2. Tokenni `bot.py` ga qo'ying
```python
# bot.py faylida shu qatorni toping:
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Va o'z tokeningizni qo'ying:
BOT_TOKEN = "7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Botni ishga tushirish
```bash
python bot.py
```

---

## 🖥️ Server (VPS) da ishlatish

### Systemd service sifatida (Linux)
```bash
# /etc/systemd/system/cvbot.service fayl yarating:
[Unit]
Description=CV Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cv_bot
ExecStart=/usr/bin/python3 /home/ubuntu/cv_bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Ishga tushirish:
sudo systemctl enable cvbot
sudo systemctl start cvbot
sudo systemctl status cvbot
```

### Screen yoki tmux bilan
```bash
screen -S cvbot
python bot.py
# Ctrl+A, D - fonda qoldirish
```

---

## 🎨 Bot imkoniyatlari

- ✅ **3 tilda**: O'zbek, Rus, Ingliz
- ✅ **PDF format** — chiroyli Europa Pass dizayni
  - Ko'k sidebar (EU flag rangi)
  - Oltin sariq detalllar
  - Chap tomonda: foto, kontakt, tillar, ko'nikmalar
  - O'ng tomonda: ism, ta'lim, tajriba, sertifikatlar
- ✅ **DOCX format** — Microsoft Word uchun
- ✅ **Foto yuklash** imkoniyati
- ✅ **Til darajalari** CEFR formatida (A1-C2)
- ✅ **Ko'p ta'lim** va **ko'p ish tajribasi** qo'shish
- ✅ **Kategoriyalangan ko'nikmalar**
- ✅ **Sertifikatlar** va **qiziqishlar**

---

## 📋 Bot qadamlari

```
/start
  → Til tanlash (O'zbek / Rus / Ingliz)
  → Rasm yuklash (ixtiyoriy)
  → Shaxsiy ma'lumotlar (ism, familiya, tug'ilgan kun...)
  → Kontakt (email, telefon, manzil)
  → Ijtimoiy tarmoqlar (LinkedIn, GitHub - ixtiyoriy)
  → Kasbiy maqsad
  → Ta'lim (bir nechta qo'shish mumkin)
  → Ish tajribasi
  → Ko'nikmalar
  → Til bilimlari
  → Sertifikatlar (ixtiyoriy)
  → Qiziqishlar (ixtiyoriy)
  → Format tanlash (PDF / DOCX / Ikkalasi)
  → Tasdiqlash
  → 📄 CV yuklab olish!
```

---

## 🛠️ Muammolar va yechimlar

**Foto ishlamayapti?**
```bash
pip install Pillow
```

**Arabic/Cyrillic harflar noto'g'ri?**
ReportLab uchun Unicode shrift qo'shish mumkin (DejaVu, FreeSans)

**Bot javob bermayapti?**
- Token to'g'riligini tekshiring
- Internet bor-yo'qligini tekshiring
- `python bot.py` qayta ishga tushiring

---

## 📞 Yordam

Bot `/cancel` - bekor qilish  
Bot `/start` - qaytadan boshlash
