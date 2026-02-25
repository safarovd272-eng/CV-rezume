"""
CV/Resume Telegram Bot
Xalqaro Europa Pass uslubida CV tayyorlaydi
Tillar: O'zbek, Rus, Ingliz
Format: PDF va DOCX
"""

import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()  # local .env fayldan o'qiydi (Railway da kerak emas)
from dotenv import load_dotenv

load_dotenv()  # .env fayldan o'qiydi (local test uchun)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from cv_generator import generate_pdf, generate_docx

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8516447460:AAG3YTQiXrtUAl4316hOFUCz0KHfYHSSgi0")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# ─── Conversation States ───────────────────────────────────────────────────────
(
    LANG, PHOTO, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, NATIONALITY,
    EMAIL, PHONE, ADDRESS, LINKEDIN, GITHUB, WEBSITE,
    OBJECTIVE, EDUCATION, WORK_EXP, SKILLS, LANGUAGES, CERTIFICATES,
    HOBBIES, FORMAT_CHOICE, CONFIRM
) = range(21)

# ─── Translations ──────────────────────────────────────────────────────────────
T = {
    'uz': {
        'welcome': "👋 Salom! Men sizga xalqaro Europa Pass uslubida professional CV tayyorlab beraman.\n\n📌 Boshlash uchun /start bosing.",
        'choose_lang': "🌐 Tilni tanlang / Choose language / Выберите язык:",
        'upload_photo': "📸 Profilingiz uchun rasm yuboring (ixtiyoriy).\n\nO'tkazib yuborish uchun /skip bosing.",
        'first_name': "👤 Ismingizni kiriting:",
        'last_name': "👤 Familiyangizni kiriting:",
        'dob': "🎂 Tug'ilgan sanangiz (Masalan: 15.03.1995):",
        'nationality': "🌍 Millatingiz (Masalan: O'zbek):",
        'email': "📧 Email manzilingiz:",
        'phone': "📱 Telefon raqamingiz (Masalan: +998901234567):",
        'address': "🏠 Manzilingiz (Shahar, Mamlakat):",
        'linkedin': "🔗 LinkedIn profilingiz (ixtiyoriy, /skip):",
        'github': "💻 GitHub profilingiz (ixtiyoriy, /skip):",
        'website': "🌐 Shaxsiy saytingiz (ixtiyoriy, /skip):",
        'objective': "🎯 Kasbiy maqsadingiz (20-30 jumla):",
        'education': (
            "🎓 Ta'lim ma'lumotlaringiz.\n"
            "Har bir ta'limni quyidagi formatda kiriting:\n"
            "Daraja | Muassasa | Yillar | GPA (ixtiyoriy)\n"
            "Misol: Bakalavr | TISU | 2018-2022 | 3.8\n\n"
            "Bir nechta ta'lim bo'lsa, har birini yangi qatordan yozing.\n"
            "Tugagach /done bosing."
        ),
        'work_exp': (
            "💼 Ish tajribangiz.\n"
            "Formatda kiriting:\n"
            "Lavozim | Kompaniya | Yillar | Qisqacha tavsif\n"
            "Misol: Dasturchi | Uzcard | 2022-2024 | Backend dasturlash, API ishlab chiqish\n\n"
            "Tajriba yo'q bo'lsa /skip, tugagach /done."
        ),
        'skills': (
            "🛠 Ko'nikmalaringiz.\n"
            "Formatda kiriting:\n"
            "Kategoriya: ko'nikma1, ko'nikma2\n"
            "Misol:\n"
            "Dasturlash: Python, Django, FastAPI\n"
            "Ma'lumotlar bazasi: PostgreSQL, Redis\n\n"
            "Tugagach /done bosing."
        ),
        'languages': (
            "🗣 Til bilimlaringiz.\n"
            "Formatda kiriting:\n"
            "Til | Daraja\n"
            "Misol:\n"
            "O'zbek | Ona tili\n"
            "Ingliz | C1\n"
            "Rus | B2\n\n"
            "Tugagach /done bosing."
        ),
        'certificates': (
            "🏆 Sertifikatlar (ixtiyoriy).\n"
            "Formatda: Nomi | Tashkilot | Yil\n"
            "Misol: IELTS 7.0 | British Council | 2023\n\n"
            "Yo'q bo'lsa /skip, tugagach /done."
        ),
        'hobbies': "⚽ Qiziqishlaringiz (ixtiyoriy, /skip):\nMisol: Kitob o'qish, Sayohat, Fotografiya",
        'choose_format': "📄 CV formatini tanlang:",
        'generating': "⏳ CV tayyorlanmoqda...",
        'done': "✅ CV tayyor! Yuklab oling 👇",
        'restart': "🔄 Yangi CV uchun /start bosing.",
        'skip_done': "/skip - o'tkazib yuborish | /done - tugatish",
        'error': "❌ Xatolik yuz berdi. Iltimos qayta urinib ko'ring.",
        'confirm': "✅ Ma'lumotlarni tasdiqlaysizmi?",
        'yes': "Ha, tasdiqlash",
        'no': "Yo'q, qaytadan",
        'pdf_and_docx': "PDF va DOCX ikkalasi",
        'only_pdf': "Faqat PDF",
        'only_docx': "Faqat DOCX",
    },
    'ru': {
        'welcome': "👋 Привет! Я помогу вам создать профессиональное CV в стиле международного Europa Pass.\n\n📌 Нажмите /start чтобы начать.",
        'choose_lang': "🌐 Выберите язык / Choose language / Tilni tanlang:",
        'upload_photo': "📸 Отправьте фото для профиля (необязательно).\n\nЧтобы пропустить, нажмите /skip.",
        'first_name': "👤 Введите ваше имя:",
        'last_name': "👤 Введите вашу фамилию:",
        'dob': "🎂 Дата рождения (Пример: 15.03.1995):",
        'nationality': "🌍 Ваша национальность (Пример: Узбек):",
        'email': "📧 Ваш Email адрес:",
        'phone': "📱 Ваш номер телефона (Пример: +998901234567):",
        'address': "🏠 Ваш адрес (Город, Страна):",
        'linkedin': "🔗 Ваш LinkedIn профиль (необязательно, /skip):",
        'github': "💻 Ваш GitHub профиль (необязательно, /skip):",
        'website': "🌐 Личный сайт (необязательно, /skip):",
        'objective': "🎯 Профессиональная цель (2-3 предложения):",
        'education': (
            "🎓 Ваше образование.\n"
            "Вводите в формате:\n"
            "Степень | Учреждение | Годы | GPA (необязательно)\n"
            "Пример: Бакалавр | ТУИТ | 2018-2022 | 3.8\n\n"
            "Несколько записей — каждая с новой строки.\n"
            "Нажмите /done чтобы завершить."
        ),
        'work_exp': (
            "💼 Ваш опыт работы.\n"
            "Формат:\n"
            "Должность | Компания | Годы | Описание\n"
            "Пример: Программист | Uzcard | 2022-2024 | Backend разработка\n\n"
            "Нет опыта — /skip, завершить — /done."
        ),
        'skills': (
            "🛠 Ваши навыки.\n"
            "Формат:\n"
            "Категория: навык1, навык2\n"
            "Пример:\n"
            "Программирование: Python, Django\n"
            "Базы данных: PostgreSQL, Redis\n\n"
            "Нажмите /done чтобы завершить."
        ),
        'languages': (
            "🗣 Знание языков.\n"
            "Формат:\n"
            "Язык | Уровень\n"
            "Пример:\n"
            "Узбекский | Родной\n"
            "Английский | C1\n"
            "Русский | Родной\n\n"
            "Нажмите /done чтобы завершить."
        ),
        'certificates': (
            "🏆 Сертификаты (необязательно).\n"
            "Формат: Название | Организация | Год\n"
            "Пример: IELTS 7.0 | British Council | 2023\n\n"
            "Нет — /skip, завершить — /done."
        ),
        'hobbies': "⚽ Хобби (необязательно, /skip):\nПример: Чтение, Путешествия, Фотография",
        'choose_format': "📄 Выберите формат CV:",
        'generating': "⏳ Создаём ваше CV...",
        'done': "✅ CV готово! Скачайте ниже 👇",
        'restart': "🔄 Для нового CV нажмите /start.",
        'skip_done': "/skip - пропустить | /done - завершить",
        'error': "❌ Произошла ошибка. Попробуйте снова.",
        'confirm': "✅ Подтвердите данные?",
        'yes': "Да, подтвердить",
        'no': "Нет, начать заново",
        'pdf_and_docx': "PDF и DOCX оба",
        'only_pdf': "Только PDF",
        'only_docx': "Только DOCX",
    },
    'en': {
        'welcome': "👋 Hello! I'll help you create a professional CV in the international Europa Pass style.\n\n📌 Press /start to begin.",
        'choose_lang': "🌐 Choose language / Tilni tanlang / Выберите язык:",
        'upload_photo': "📸 Send your profile photo (optional).\n\nPress /skip to skip.",
        'first_name': "👤 Enter your first name:",
        'last_name': "👤 Enter your last name:",
        'dob': "🎂 Date of birth (Example: 15.03.1995):",
        'nationality': "🌍 Your nationality (Example: Uzbek):",
        'email': "📧 Your email address:",
        'phone': "📱 Your phone number (Example: +998901234567):",
        'address': "🏠 Your address (City, Country):",
        'linkedin': "🔗 Your LinkedIn profile (optional, /skip):",
        'github': "💻 Your GitHub profile (optional, /skip):",
        'website': "🌐 Personal website (optional, /skip):",
        'objective': "🎯 Professional objective (2-3 sentences):",
        'education': (
            "🎓 Your education.\n"
            "Enter in format:\n"
            "Degree | Institution | Years | GPA (optional)\n"
            "Example: Bachelor | TUIT | 2018-2022 | 3.8\n\n"
            "Multiple entries — each on a new line.\n"
            "Press /done when finished."
        ),
        'work_exp': (
            "💼 Your work experience.\n"
            "Format:\n"
            "Position | Company | Years | Description\n"
            "Example: Developer | Uzcard | 2022-2024 | Backend development, API design\n\n"
            "No experience — /skip, finished — /done."
        ),
        'skills': (
            "🛠 Your skills.\n"
            "Format:\n"
            "Category: skill1, skill2\n"
            "Example:\n"
            "Programming: Python, Django, FastAPI\n"
            "Databases: PostgreSQL, Redis\n\n"
            "Press /done when finished."
        ),
        'languages': (
            "🗣 Language skills.\n"
            "Format:\n"
            "Language | Level\n"
            "Example:\n"
            "Uzbek | Native\n"
            "English | C1\n"
            "Russian | B2\n\n"
            "Press /done when finished."
        ),
        'certificates': (
            "🏆 Certificates (optional).\n"
            "Format: Name | Organization | Year\n"
            "Example: IELTS 7.0 | British Council | 2023\n\n"
            "None — /skip, finished — /done."
        ),
        'hobbies': "⚽ Hobbies (optional, /skip):\nExample: Reading, Travel, Photography",
        'choose_format': "📄 Choose CV format:",
        'generating': "⏳ Generating your CV...",
        'done': "✅ CV is ready! Download below 👇",
        'restart': "🔄 Press /start for a new CV.",
        'skip_done': "/skip - skip | /done - finish",
        'error': "❌ An error occurred. Please try again.",
        'confirm': "✅ Confirm your data?",
        'yes': "Yes, confirm",
        'no': "No, start over",
        'pdf_and_docx': "Both PDF & DOCX",
        'only_pdf': "PDF only",
        'only_docx': "DOCX only",
    }
}


def t(context: ContextTypes.DEFAULT_TYPE, key: str) -> str:
    lang = context.user_data.get('lang', 'uz')
    return T[lang].get(key, T['en'].get(key, key))


def get_data(context, key, default=''):
    return context.user_data.get(key, default)


def append_list_data(context, key, value):
    if key not in context.user_data:
        context.user_data[key] = []
    context.user_data[key].append(value)


# ─── Handlers ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]]
    await update.message.reply_text(
        T['uz']['welcome'] + "\n\n" + T['ru']['welcome'] + "\n\n" + T['en']['welcome'],
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return LANG


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "O'zbek" in text or "Uzbek" in text:
        context.user_data['lang'] = 'uz'
    elif "Русский" in text or "Russian" in text:
        context.user_data['lang'] = 'ru'
    else:
        context.user_data['lang'] = 'en'

    await update.message.reply_text(
        t(context, 'upload_photo'),
        reply_markup=ReplyKeyboardRemove()
    )
    return PHOTO


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        photo_path = f"/tmp/cv_photo_{update.effective_user.id}.jpg"
        await file.download_to_drive(photo_path)
        context.user_data['photo'] = photo_path
    await update.message.reply_text(t(context, 'first_name'))
    return FIRST_NAME


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo'] = None
    await update.message.reply_text(t(context, 'first_name'))
    return FIRST_NAME


async def get_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['first_name'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'last_name'))
    return LAST_NAME


async def get_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['last_name'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'dob'))
    return DATE_OF_BIRTH


async def get_dob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['dob'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'nationality'))
    return NATIONALITY


async def get_nationality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nationality'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'email'))
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'phone'))
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'address'))
    return ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['address'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'linkedin'))
    return LINKEDIN


async def get_linkedin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['linkedin'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'github'))
    return GITHUB


async def skip_linkedin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['linkedin'] = ''
    await update.message.reply_text(t(context, 'github'))
    return GITHUB


async def get_github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['github'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'website'))
    return WEBSITE


async def skip_github(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['github'] = ''
    await update.message.reply_text(t(context, 'website'))
    return WEBSITE


async def get_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['website'] = update.message.text.strip()
    await update.message.reply_text(t(context, 'objective'))
    return OBJECTIVE


async def skip_website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['website'] = ''
    await update.message.reply_text(t(context, 'objective'))
    return OBJECTIVE


async def get_objective(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['objective'] = update.message.text.strip()
    context.user_data['education_list'] = []
    await update.message.reply_text(t(context, 'education'))
    return EDUCATION


async def get_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if '|' in text:
        parts = [p.strip() for p in text.split('\n') if '|' in p]
        for p in parts:
            context.user_data.setdefault('education_list', []).append(p)
    await update.message.reply_text(
        f"✅ Qo'shildi! Yana qo'shish uchun yozing yoki /done bosing.\n{t(context, 'skip_done')}"
    )
    return EDUCATION


async def done_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault('work_list', [])
    await update.message.reply_text(t(context, 'work_exp'))
    return WORK_EXP


async def get_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if '|' in text:
        parts = [p.strip() for p in text.split('\n') if '|' in p]
        for p in parts:
            context.user_data.setdefault('work_list', []).append(p)
    await update.message.reply_text(
        f"✅ Qo'shildi! Yana qo'shish uchun yozing yoki /done bosing.\n{t(context, 'skip_done')}"
    )
    return WORK_EXP


async def skip_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['work_list'] = []
    context.user_data.setdefault('skills_list', [])
    await update.message.reply_text(t(context, 'skills'))
    return SKILLS


async def done_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault('skills_list', [])
    await update.message.reply_text(t(context, 'skills'))
    return SKILLS


async def get_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = [l.strip() for l in text.split('\n') if ':' in l]
    for line in lines:
        context.user_data.setdefault('skills_list', []).append(line)
    await update.message.reply_text(
        f"✅ Qo'shildi! Yana qo'shish yoki /done bosing."
    )
    return SKILLS


async def done_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault('lang_list', [])
    await update.message.reply_text(t(context, 'languages'))
    return LANGUAGES


async def get_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = [p.strip() for p in text.split('\n') if '|' in p]
    for p in parts:
        context.user_data.setdefault('lang_list', []).append(p)
    await update.message.reply_text(
        f"✅ Qo'shildi! Yana qo'shish yoki /done bosing."
    )
    return LANGUAGES


async def done_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault('cert_list', [])
    await update.message.reply_text(t(context, 'certificates'))
    return CERTIFICATES


async def get_certificates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = [p.strip() for p in text.split('\n') if '|' in p]
    for p in parts:
        context.user_data.setdefault('cert_list', []).append(p)
    await update.message.reply_text(f"✅ Qo'shildi! /done bosing.")
    return CERTIFICATES


async def skip_certificates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['cert_list'] = []
    await update.message.reply_text(t(context, 'hobbies'))
    return HOBBIES


async def done_certificates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(t(context, 'hobbies'))
    return HOBBIES


async def get_hobbies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['hobbies'] = update.message.text.strip()
    return await show_format_choice(update, context)


async def skip_hobbies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['hobbies'] = ''
    return await show_format_choice(update, context)


async def show_format_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(t(context, 'pdf_and_docx'), callback_data='both')],
        [InlineKeyboardButton(t(context, 'only_pdf'), callback_data='pdf')],
        [InlineKeyboardButton(t(context, 'only_docx'), callback_data='docx')],
    ]
    await update.message.reply_text(
        t(context, 'choose_format'),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return FORMAT_CHOICE


async def handle_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['format'] = query.data

    # Show summary
    data = context.user_data
    summary = (
        f"👤 *{data.get('first_name', '')} {data.get('last_name', '')}*\n"
        f"📧 {data.get('email', '')}\n"
        f"📱 {data.get('phone', '')}\n"
        f"📚 Ta'lim: {len(data.get('education_list', []))} ta\n"
        f"💼 Tajriba: {len(data.get('work_list', []))} ta\n"
        f"🛠 Ko'nikmalar: {len(data.get('skills_list', []))} kategoriya\n"
        f"🗣 Tillar: {len(data.get('lang_list', []))} ta\n"
    )

    confirm_keyboard = [
        [InlineKeyboardButton(t(context, 'yes'), callback_data='confirm_yes')],
        [InlineKeyboardButton(t(context, 'no'), callback_data='confirm_no')],
    ]
    await query.edit_message_text(
        f"{t(context, 'confirm')}\n\n{summary}",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(confirm_keyboard)
    )
    return CONFIRM


async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'confirm_no':
        await query.edit_message_text("🔄 Qaytadan boshlash uchun /start bosing.")
        return ConversationHandler.END

    await query.edit_message_text(t(context, 'generating'))

    try:
        data = context.user_data
        fmt = data.get('format', 'both')
        user_id = update.effective_user.id

        pdf_path = None
        docx_path = None

        if fmt in ('pdf', 'both'):
            pdf_path = f"/tmp/cv_{user_id}.pdf"
            generate_pdf(data, pdf_path)

        if fmt in ('docx', 'both'):
            docx_path = f"/tmp/cv_{user_id}.docx"
            generate_docx(data, docx_path)

        await query.edit_message_text(t(context, 'done'))

        chat_id = update.effective_chat.id

        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    filename=f"{data.get('first_name', 'CV')}_{data.get('last_name', '')}_CV.pdf",
                    caption="📄 CV - PDF format"
                )

        if docx_path and os.path.exists(docx_path):
            with open(docx_path, 'rb') as f:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    filename=f"{data.get('first_name', 'CV')}_{data.get('last_name', '')}_CV.docx",
                    caption="📝 CV - Word format"
                )

        await context.bot.send_message(chat_id=chat_id, text=t(context, 'restart'))

    except Exception as e:
        logger.error(f"Error generating CV: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t(context, 'error')
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi. Qayta boshlash uchun /start bosing.")
    return ConversationHandler.END


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
            PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo),
                CommandHandler('skip', skip_photo),
            ],
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_first_name)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_last_name)],
            DATE_OF_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dob)],
            NATIONALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nationality)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            LINKEDIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_linkedin),
                CommandHandler('skip', skip_linkedin),
            ],
            GITHUB: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_github),
                CommandHandler('skip', skip_github),
            ],
            WEBSITE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_website),
                CommandHandler('skip', skip_website),
            ],
            OBJECTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_objective)],
            EDUCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_education),
                CommandHandler('done', done_education),
            ],
            WORK_EXP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_work),
                CommandHandler('skip', skip_work),
                CommandHandler('done', done_work),
            ],
            SKILLS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_skills),
                CommandHandler('done', done_skills),
            ],
            LANGUAGES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_languages),
                CommandHandler('done', done_languages),
            ],
            CERTIFICATES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_certificates),
                CommandHandler('skip', skip_certificates),
                CommandHandler('done', done_certificates),
            ],
            HOBBIES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_hobbies),
                CommandHandler('skip', skip_hobbies),
            ],
            FORMAT_CHOICE: [CallbackQueryHandler(handle_format)],
            CONFIRM: [CallbackQueryHandler(handle_confirm)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)

    print("✅ Bot ishga tushdi!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
