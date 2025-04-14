import logging
from aiogram import Router, types

# Ініціалізація роутера
router = Router()
logger = logging.getLogger(__name__)

@router.message()
async def handle_keyboard_input(message: types.Message):
    user_input = message.text
    user_id = message.from_user.id

    # Логування дії користувача
    logger.info(f"Користувач {user_id} натиснув кнопку: {user_input}")

    # Реакція на натискання кнопок
    if user_input == "🛍️ Каталог":
        await message.answer("Каталог кондиціонерів ще в розробці. Зачекайте на оновлення! 🌟")
    elif user_input == "📚 Довідник":
        await message.answer("Довідник ще не готовий. Ми вже працюємо над ним! 📖")
    elif user_input == "🔍 Пошук":
        await message.answer("Майбутній ШІ поки що спить. Зачекайте, ми його скоро розбудимо! 🤖")
    elif user_input == "❓ Допомога":
        await message.answer("🛠 <b>Доступні команди:</b>\n\n"
                             "/start - Почати роботу з ботом\n"
                             "/help - Список доступних функцій\n"
                             "/info - Інформація про бота\n",
                             parse_mode="HTML")
    else:
        await message.answer("Я поки що не розумію цю команду. 🙃")