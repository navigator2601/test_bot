from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.connection import Database
from database import queries

async def create_brands_keyboard():
    """Створює inline клавіатуру зі списком брендів."""
    db = Database()
    await db.connect()
    brands = await db.fetch(queries.GET_BRANDS_WITH_MODEL_COUNT)
    await db.disconnect()

    keyboard = []
    for brand in brands:
        keyboard.append([InlineKeyboardButton(text=f"{brand['brand_name']} ({brand['model_count']})", callback_data=f"brand_{brand['brand_id']}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def create_types_keyboard(brand_id: int):
    """Створює inline клавіатуру зі списком типів для обраного бренду."""
    db = Database()
    await db.connect()
    types = await db.fetch(queries.GET_TYPES_BY_BRAND_WITH_MODEL_COUNT, brand_id)
    await db.disconnect()

    keyboard = []
    for type_item in types:
        keyboard.append([InlineKeyboardButton(text=f"{type_item['type_name']} ({type_item['model_count']})", callback_data=f"type_{brand_id}_{type_item['type_id']}")])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_brands")]) # Додано кнопку "Назад"
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def create_models_keyboard(brand_id: int, type_id: int):
    """Створює inline клавіатуру зі списком моделей для обраного бренду та типу."""
    db = Database()
    await db.connect()
    models = await db.fetch(queries.GET_MODELS_BY_BRAND_AND_TYPE, brand_id, type_id)
    await db.disconnect()

    keyboard = []
    for model in models:
        keyboard.append([InlineKeyboardButton(text=model['model_name'], callback_data=f"model_{brand_id}_{type_id}_{model['id']}")])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_types_{brand_id}")]) # Додано кнопку "Назад"
    return InlineKeyboardMarkup(inline_keyboard=keyboard)