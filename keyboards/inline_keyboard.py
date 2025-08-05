# Файл: keyboards/inline_keyboard.py
# Призначення: Створення та управління Inline-клавіатурами для бота.
# Містить функції для динамічної генерації кнопок на основі даних з БД.

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict

async def get_brands_inline_keyboard(brands: List[Dict]) -> InlineKeyboardMarkup:
    """
    Генерує Inline-клавіатуру зі списком брендів та кількістю моделей.
    """
    builder = InlineKeyboardBuilder()
    for brand in brands:
        brand_name = brand.get("Бренд", "N/A")
        model_count = brand.get("Кількість моделей", 0)
        button_text = f"{brand_name} ({model_count})"
        callback_data = f"brand_{brand_name}"
        builder.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))
    builder.adjust(1)
    return builder.as_markup()

async def get_models_inline_keyboard(models: List[Dict]) -> InlineKeyboardMarkup:
    """
    Генерує Inline-клавіатуру зі списком моделей та кнопкою повернення.
    """
    builder = InlineKeyboardBuilder()
    for model in models:
        model_name = model.get("Модель", "N/A")
        # Ми змінюємо callback_data, щоб вказати, що це модель, і додати її назву
        callback_data = f"model_details_{model_name}" 
        builder.add(InlineKeyboardButton(text=model_name, callback_data=callback_data))
    builder.adjust(1)
    
    # Додаємо кнопку повернення
    builder.row(InlineKeyboardButton(text="⬅️ До списку брендів", callback_data="back_to_brands"))
    
    return builder.as_markup()

# ОНОВЛЕНО: ТЕПЕР МИ ОТРИМУЄМО НАЗВУ БРЕНДУ, ЩОБ ПОВЕРНУТИСЯ
async def get_model_info_keyboard(model_name: str, brand_name: str) -> InlineKeyboardMarkup:
    """
    Генерує Inline-клавіатуру з категоріями інформації про модель.
    """
    builder = InlineKeyboardBuilder()

    # Створюємо кнопки з категоріями
    builder.row(InlineKeyboardButton(text="Загальні характеристики", callback_data=f"info_general_{model_name}"))
    builder.row(InlineKeyboardButton(text="Функції", callback_data=f"info_functions_{model_name}"))
    builder.row(InlineKeyboardButton(text="Технічні параметри", callback_data=f"info_tech_{model_name}"))
    builder.row(InlineKeyboardButton(text="Повна інформація", callback_data=f"info_full_{model_name}"))
    
    # Додаємо кнопку повернення до списку моделей
    callback_data = f"back_to_models_{brand_name}"
    builder.row(InlineKeyboardButton(text="⬅️ До списку моделей", callback_data=callback_data))
    
    return builder.as_markup()