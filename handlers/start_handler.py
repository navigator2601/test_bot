from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext
from handlers.common import get_greeting

async def start(update: Update, context: CallbackContext) -> None:
    user_name = update.effective_user.first_name or "користувач"
    greeting = get_greeting()

    keyboard = [
        ['ℹ️ Інформація', '⚙️ Налаштування'],
        ['📞 Підтримка'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome_message = (
        f"{greeting}, {user_name}!\n\n"
        "Для супроводу натисніть потрібну кнопку внизу.\n"
        "Для швидкого пошуку просто введіть будь-яку інформацію:\n"
        "- Модель кондиціонера\n"
        "- Потужність кондиціонера\n"
        "- Розміри блоків\n"
        "- Типи кондиціонерів"
    )

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

start_handler = CommandHandler("start", start)
