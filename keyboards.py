from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

def main_menu() -> ReplyKeyboardMarkup:
    """Головне меню 2×2 з кнопками та піктограмами"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Каталог"), KeyboardButton(text="🛠️ Технічна інформація")],
            [KeyboardButton(text="⚠️ Коди помилок"), KeyboardButton(text="❓ FAQ")]
        ],
        resize_keyboard=True  # Зменшує розмір клавіатури для зручності
    )

def catalog_menu() -> ReplyKeyboardMarkup:
    """Компактне підменю для кнопки Каталог (2×2)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📜 Вибір зі списку",
                    web_app=WebAppInfo(url="https://navigator2601.github.io/test_bot/webapp/")  # URL вашого веб-додатка
                ),
                KeyboardButton(text="🔍 Пошук по бренду")
            ],
            [KeyboardButton(text="📂 Пошук по типу"), KeyboardButton(text="⬅️ Назад")]  # Оновлений формат
        ],
        resize_keyboard=True
    )