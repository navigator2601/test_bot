from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    """Компактне меню 2×2 з кнопками"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог"), KeyboardButton(text="Технічна інформація")],
            [KeyboardButton(text="Коди помилок"), KeyboardButton(text="FAQ")]
        ],
        resize_keyboard=True  # Зменшує розмір клавіатури для зручності
    )