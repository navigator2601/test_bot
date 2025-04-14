from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_reply_keyboard() -> ReplyKeyboardMarkup:
    # Створюємо кнопки
    buttons = [
        [KeyboardButton(text="🛍️ Каталог"), KeyboardButton(text="📚 Довідник")],  # Перший ряд
        [KeyboardButton(text="🔍 Пошук"), KeyboardButton(text="❓ Допомога")]  # Другий ряд
    ]

    # Створюємо клавіатуру
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,  # Робить кнопки компактними
        one_time_keyboard=False  # Клавіатура залишається на екрані
    )
    return keyboard