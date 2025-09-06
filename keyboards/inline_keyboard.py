# keyboards/inline_keyboard.py

from typing import List, Dict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callback_factories import CatalogCallback


def get_brands_inline_keyboard(brands: List[Dict]) -> InlineKeyboardMarkup:
    """
    Створює інлайн-клавіатуру зі списком брендів з кількістю моделей.
    """
    builder = InlineKeyboardBuilder()
    for brand in brands:
        brand_id = brand.get('brand_id')
        brand_name = brand.get('brand_name')
        model_count = brand.get('model_count')

        if brand_name is None or brand_id is None:
            continue

        button_text = f"{brand_name} ({model_count if model_count is not None else 0})"
        callback_data = CatalogCallback(action="select_brand", brand_id=brand_id, brand_name=brand_name).pack()

        builder.button(text=button_text, callback_data=callback_data)

    builder.row(InlineKeyboardButton(text="⬅️ На головну", callback_data="main_menu_return"))
    builder.adjust(1)
    return builder.as_markup()


def get_models_inline_keyboard(models: List[Dict], brand_name: str) -> InlineKeyboardMarkup:
    """
    Створює інлайн-клавіатуру зі списком моделей для обраного бренду.
    """
    builder = InlineKeyboardBuilder()
    for model in models:
        model_id = model.get('model_id')
        model_name = model.get('Модель')

        if model_name is None or model_id is None:
            continue
        
        callback_data = CatalogCallback(action="select_model", brand_name=brand_name, model_id=model_id).pack()
        builder.button(text=model_name, callback_data=callback_data)

    builder.row(InlineKeyboardButton(text="⬅️ Назад до брендів", callback_data=CatalogCallback(action="back_to_brands").pack()))
    builder.adjust(1)
    return builder.as_markup()


def get_model_details_keyboard() -> InlineKeyboardMarkup:
    """
    Створює інлайн-клавіатуру для сторінки деталей моделі.
    """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад до моделей", callback_data="back_to_models"))
    builder.adjust(1)
    return builder.as_markup()