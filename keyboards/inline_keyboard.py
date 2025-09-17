# відносний шлях до файлу: keyboards/inline_keyboard.py
# Призначення: Функції для створення інлайн-клавіатур.

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict

async def get_brands_inline_keyboard(brands: List[Dict]) -> InlineKeyboardMarkup:
    """
    Створює інлайн-клавіатуру з кнопками для кожного бренду.
    Кожна кнопка має назву бренду та кількість моделей.
    """
    keyboard_buttons = []
    current_row = []
    
    # Створення кнопок для кожного бренду.
    # Додаємо по дві кнопки в ряду для компактності.
    for brand in brands:
        brand_name = brand['Бренд']
        model_count = brand['Кількість моделей']
        button_text = f"{brand_name} ({model_count})"
        callback_data = f"brand_{brand_name}"
        
        current_row.append(InlineKeyboardButton(text=button_text, callback_data=callback_data))
        
        # Перевіряємо, чи поточний рядок має 2 кнопки. Якщо так - додаємо його до загального списку
        # та очищаємо для наступних кнопок.
        if len(current_row) == 2:
            keyboard_buttons.append(current_row)
            current_row = []

    # Якщо після циклу в current_row залишилася одна кнопка, додаємо її до загального списку.
    if current_row:
        keyboard_buttons.append(current_row)

    # Додаємо кнопку "В головне меню" в кінець, на весь рядок
    keyboard_buttons.append(
        [InlineKeyboardButton(text="⬅️ В головне меню", callback_data="back_to_main_menu")]
    )
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


async def get_models_inline_keyboard(models: List[Dict]) -> InlineKeyboardMarkup:
    """
    Створює інлайн-клавіатуру з кнопками для кожної моделі.
    Кожна кнопка має назву моделі.
    """
    keyboard_buttons = []
    current_row = []
    
    # Створення кнопок для кожної моделі
    for model in models:
        model_name = model.get('Модель', 'N/A')
        model_id = model.get('model_id')
        brand_name = model.get('brand_name')

        callback_data = f"model_{brand_name}_{model_id}"
        
        current_row.append(InlineKeyboardButton(text=model_name, callback_data=callback_data))

        if len(current_row) == 2:
            keyboard_buttons.append(current_row)
            current_row = []
    
    if current_row:
        keyboard_buttons.append(current_row)

    # Додаємо кнопку "В головне меню" в кінець
    keyboard_buttons.append(
        [InlineKeyboardButton(text="⬅️ В головне меню", callback_data="back_to_main_menu")]
    )
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


async def get_back_to_models_keyboard(brand_name: str) -> InlineKeyboardMarkup:
    """
    Створює інлайн-клавіатуру з кнопкою "Назад до моделей".
    
    :param brand_name: Назва бренду, до якого потрібно повернутися.
    :return: Об'єкт InlineKeyboardMarkup з однією кнопкою.
    """
    callback_data = f"brand_{brand_name}"
    keyboard_buttons = [
        [InlineKeyboardButton(text=f"⬅️ Назад до моделей {brand_name}", callback_data=callback_data)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)