import asyncio
import asyncpg
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 📌 Дані для підключення до PostgreSQL
DB_URL = "postgresql://neondb_owner:npg_dhwrDX6O1keB@ep-round-star-a9r38wl3-pooler.gwc.azure.neon.tech/neondb"

# 📌 Функція підключення до БД та отримання даних
async def fetch_data(query):
    conn = await asyncpg.connect(DB_URL)
    rows = await conn.fetch(query)
    await conn.close()
    return rows

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
#                [InlineKeyboardButton("🔙 Назад", callback_data='back')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ℹ️ Інформація:", reply_markup=reply_markup)

# 📌 Отримання списку марок кондиціонерів
async def get_brands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    brands = await fetch_data("SELECT id, name FROM cond_brand")  # Запит до таблиці
    keyboard = [[InlineKeyboardButton(f"✅ {b['name']}", callback_data=f"brand_{b['id']}")] for b in brands]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text("📋 **Марки кондиціонерів:**", reply_markup=reply_markup)

# 📌 Отримання списку моделей для конкретної марки кондиціонера
async def get_models(update: Update, context: ContextTypes.DEFAULT_TYPE, brand_id: int) -> None:
    models = await fetch_data(f"SELECT indoor_unit_model, outdoor_unit_model FROM cond_models WHERE abbr = '{brand_id}'")
    model_list = "\n".join([f"🏠 Внутрішній блок: {m['indoor_unit_model']}\n🌳 Зовнішній блок: {m['outdoor_unit_model']}" for m in models]) if models else "❌ Дані відсутні."
    await update.callback_query.message.reply_text(f"📋 **Моделі кондиціонерів:**\n{model_list}", parse_mode="Markdown")

# 📌 Отримання типів фреонів
async def get_freon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    freons = await fetch_data("SELECT name, chemical_name FROM freons")
    freon_list = "\n".join([f"❄️ {f['name']} – {f['chemical_name']}" for f in freons]) if freons else "❌ Дані відсутні."
    await update.callback_query.message.reply_text(f"❄️ **Типи фреонів:**\n{freon_list}", parse_mode="Markdown")

# 📌 Обробка натискання кнопок
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'brands':
        await get_brands(update, context)
    elif query.data == 'freon':
        await get_freon(update, context)
    elif query.data.startswith('brand_'):
        brand_id = query.data.split('_')[1]
        await get_models(update, context, brand_id)
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
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        token = "8177185933:AAGvnm0JmuTxucr8VqU0nzGd4WrNkn5VHpU"  # Ваш токен

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ Бот запущено...")
    app.run_polling()

if __name__ == '__main__':
    main()