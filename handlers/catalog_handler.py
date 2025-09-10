# Файл: handlers/catalog_handler.py

import logging
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message
from aiogram.enums.parse_mode import ParseMode
from asyncpg import Pool
from aiogram.fsm.context import FSMContext

from database.db_search_functions import (
    get_brands_with_model_count,
    get_models_by_brand,
    get_model_details_by_id,
    format_model_details
)
from keyboards.inline_keyboard import (
    get_brands_inline_keyboard,
    get_models_inline_keyboard,
    get_model_details_keyboard
)

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "📚 Каталог")
async def show_catalog_handler(message: Message, db_pool: Pool, state: FSMContext):
    """
    Показує список брендів кондиціонерів з кількістю моделей.
    """
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) натиснув кнопку '📚 Каталог'.")
    
    brands = await get_brands_with_model_count(db_pool)
    
    if brands:
        keyboard = await get_brands_inline_keyboard(brands)
        await message.answer(
            "<b>Бренди кондиціонерів:</b>\nОберіть бренд для перегляду моделей.",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer("❌ На жаль, бренди не знайдено.")

@router.callback_query(F.data.startswith("brand_"))
async def show_models_handler(callback_query: CallbackQuery, db_pool: Pool, state: FSMContext):
    """
    Показує список моделей для обраного бренду.
    """
    brand_name = callback_query.data.split('brand_')[1]
    
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) обрав бренд '{brand_name}'.")

    models = await get_models_by_brand(db_pool, brand_name)
    
    if models:
        keyboard = await get_models_inline_keyboard(models, brand_name)
        await callback_query.message.edit_text(
            text=f"📦 <b>Моделі {brand_name}:</b>\nОберіть модель для перегляду деталей.",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await callback_query.message.edit_text(
            text=f"❌ На жаль, моделі бренду '{brand_name}' не знайдено.",
            reply_markup=None,
            parse_mode=ParseMode.HTML
        )
    
    await callback_query.answer()


@router.callback_query(F.data.startswith("model_details_"))
async def model_details_handler(callback_query: CallbackQuery, db_pool: Pool, state: FSMContext):
    """
    Показує повну інформацію про обрану модель.
    """
    try:
        model_id_str = callback_query.data.split('model_details_')[1]
        model_id = int(model_id_str)
    except (IndexError, ValueError):
        await callback_query.answer("Помилка при отриманні ID моделі.", show_alert=True)
        return

    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) обрав модель з ID: {model_id}.")

    model_details = await get_model_details_by_id(db_pool, model_id)
    
    if model_details:
        formatted_text = format_model_details(model_details)
        brand_name = model_details.get("Бренд", "Бренд")  # Отримуємо назву бренду для кнопки повернення
        keyboard = await get_model_details_keyboard(brand_name)
        await callback_query.message.edit_text(
            text=formatted_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await callback_query.message.edit_text(
            text="❌ На жаль, інформацію про цю модель не знайдено.",
            reply_markup=None,
            parse_mode=ParseMode.HTML
        )
    
    await callback_query.answer()


@router.callback_query(F.data.startswith("back_to_models_"))
async def back_to_models_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє натискання кнопки "Назад" у списку моделей.
    """
    try:
        brand_name = callback_query.data.split('back_to_models_')[1]
    except IndexError:
        await callback_query.answer("Помилка повернення.", show_alert=True)
        return

    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) повернувся до списку моделей бренду '{brand_name}'.")

    models = await get_models_by_brand(db_pool, brand_name)
    keyboard = await get_models_inline_keyboard(models, brand_name)
    
    await callback_query.message.edit_text(
        text=f"📦 <b>Моделі {brand_name}:</b>\nОберіть модель для перегляду деталей.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    
    await callback_query.answer()

@router.callback_query(F.data == "back_to_brands")
async def back_to_brands_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє натискання кнопки "Назад" до списку брендів.
    """
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) повернувся до списку брендів.")
    
    brands = await get_brands_with_model_count(db_pool)
    keyboard = await get_brands_inline_keyboard(brands)
    
    await callback_query.message.edit_text(
        text="<b>Бренди кондиціонерів:</b>\nОберіть бренд для перегляду моделей.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

    await callback_query.answer()