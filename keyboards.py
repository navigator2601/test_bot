from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    """
    Головне меню 2×2 з кнопками.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Каталог"), KeyboardButton(text="🛠️ Технічна інформація")],
            [KeyboardButton(text="⚠️ Коди помилок"), KeyboardButton(text="❓ FAQ")]
        ],
        resize_keyboard=True  # Зменшує розмір клавіатури для зручності
    )

def catalog_menu(brands: list[tuple[str, int]]) -> ReplyKeyboardMarkup:
    """
    Динамічне меню для брендів.
    :param brands: Список брендів та кількість моделей у форматі [(brand_name, model_count), ...].
    """
    keyboard = [
        [KeyboardButton(text=f"{brand_name} ({model_count})")] for brand_name, model_count in brands
    ]
    # Додаємо кнопку "Назад" в кінці
    keyboard.append([KeyboardButton(text="⬅️ Назад")])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )