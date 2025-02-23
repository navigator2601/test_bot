#!/bin/bash

# Клонування репозиторію
git clone https://github.com/navigator2601/Kondiki.git
cd Kondiki

# Створення та активація віртуального середовища
python3 -m venv venv
source venv/bin/activate

# Оновлення pip
pip install --upgrade pip

# Створення файлу runtime.txt
echo "python-3.9.12" > runtime.txt

# Створення файлу requirements.txt
cat <<EOT > requirements.txt
Flask==2.0.2
gunicorn==20.1.0
python-telegram-bot==13.7
asyncpg==0.30.0
EOT

# Створення файлу Procfile
echo "web: python bot_menu.py" > Procfile

# Створення файлу bot_menu.py
cat <<EOT > bot_menu.py
import asyncio
import asyncpg
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 📌 Дані для підключення до PostgreSQL
DB_URL = "postgresql://neondb_owner:npg_dhwrDX6O1keB@ep-round-star-a9r38wl3-pooler.gwc.azure.neon.tech/neondb"

# 📌 Функція підключення до БД та отримання даних
async def fetch_data(query):
    try:
        conn = await asyncpg.connect(DB_URL)
        rows = await conn.fetch(query)
        await conn.close()
        return rows
    except Exception as e:
        logger.error(f"Помилка підключення до БД: ${e}")
        return []

# 📌 Головне меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [['ℹ️ Інформація', '⚙️ Налаштування'],
                ['📞 Підтримка', '🔙 Назад'],
                ['Просто велика кнопка']]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Чіназес! Просто імбово що ти підключився. Будемо чілитися разом", reply_markup=reply_markup)

# 📌 Меню "ℹ️ Інформація"
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("📋 Марки кондиціонерів", callback_data='brands')],
                [InlineKeyboardButton("❄️ Типи фреонів", callback_data='freon')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ℹ️ Інформація:", reply_markup=reply_markup)

# 📌 Отримання списку марок кондиціонерів
async def get_brands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    brands = await fetch_data("SELECT name FROM cond_brand")  # Запит до таблиці
    brands_list = "\n".join([f"✅ {b['name']}" for b in brands]) if brands else "❌ Дані відсутні."
    await update.callback_query.message.reply_text(f"📋 **Марки кондиціонерів:**\n{brands_list}", parse_mode="Markdown")

# 📌 Отримання типів фреонів
async def get_freon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    freons = await fetch_data("SELECT name, chemical_name FROM freons")
    freon_list = "\n".join([f"❄️ {f['name']} – {f['chemical_name']}"] for f in freons) if freons else "❌ Дані відсутні."
    await update.callback_query.message.reply_text(f"❄️ **Типи фреонів:**\n{freon_list}", parse_mode="Markdown")

# 📌 Обробка натискання кнопок
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'brands':
        await get_brands(update, context)
    elif query.data == 'freon':
        await get_freon(update, context)
    elif query.data == 'back':
        await start(update, context)

# 📌 Обробка повідомлень
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text == "ℹ️ Інформація":
        await info(update, context)
    elif text == "⚙️ Налаштування":
        await update.message.reply_text("⚙️ Тут колись плануються налаштування.")
    elif text == "📞 Підтримка":
        await update.message.reply_text("📞 Ну може колись і підтримаємо, але зараз все в режимі розробки")
    elif text == "🔙 Назад":
        await start(update, context)
    elif text == "Просто велика кнопка":
        await update.message.reply_text("Якщо вона велика, то це не означає що її нада тицяти. Пон?")

# 📌 Головна функція
def main():
    app = Application.builder().token("8177185933:AAGvnm0JmuTxucr8VqU0nzGd4WrNkn5VHpU").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("✅ Бот запущено...")
    app.run_polling()

if __name__ == '__main__':
    main()
EOT

# Встановлення залежностей
pip install -r requirements.txt

# Запуск бота локально для перевірки
python bot_menu.py

# Увійдіть у свій обліковий запис Heroku
heroku login

# Додайте віддалений сховище Heroku, якщо ще не додано
heroku git:remote -a kondiki

# Додайте змінні середовища для токену Telegram бота
heroku config:set TELEGRAM_BOT_TOKEN=8177185933:AAGvnm0JmuTxucr8VqU0nzGd4WrNkn5VHpU

# Запуште код до Heroku
git add runtime.txt requirements.txt Procfile bot_menu.py
git commit -m "Initial commit with stable Python version"
git push heroku main

# Перевірте журнали Heroku для отримання додаткової інформації про можливі помилки
heroku logs -a kondiki --tail