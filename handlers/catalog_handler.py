# handlers/catalog_handler.py

import logging
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove # <-- Додано
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
from keyboards.callback_factories import CatalogCallback

router = Router()
logger = logging.getLogger(__name__)

# НОВИЙ ОБРОБНИК: Вибір бренду та виведення моделей
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
        keyboard = get_brands_inline_keyboard(brands)
        await message.answer(
            "<b>Бренди кондиціонерів:</b>\nОберіть бренд для перегляду моделей.",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer("На жаль, бренди не знайдено.")

@router.callback_query(CatalogCallback.filter(F.action == "select_brand"))
async def select_brand_handler(
    callback_query: CallbackQuery,
    callback_data: CatalogCallback,
    db_pool: Pool
):
    """
    Обробляє натискання на кнопку бренду, виводить список моделей для цього бренду.
    """
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    brand_id = callback_data.brand_id
    brand_name = callback_data.brand_name
    
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) обрав бренд '{brand_name}' з ID: {brand_id}.")
    
    models = await get_models_by_brand(db_pool, brand_id)
    
    if models:
        # Ваш попередній код
        # ...
        model_count = len(models)
        model_word = "модель" if model_count == 1 else "моделі" if 1 < model_count < 5 else "моделей"
        
        message_text = (
            f"⚡ Сканування завершено!\n"
            f"У бренді <b>{brand_name}</b> знайдено {model_count} {model_word}:"
        )
        
        keyboard = get_models_inline_keyboard(models, brand_name)
        
        await callback_query.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        
        await callback_query.answer()
    else:
        await callback_query.message.edit_text(
            text=f"На жаль, моделі для бренду <b>{brand_name}</b> не знайдено.",
            reply_markup=get_brands_inline_keyboard(await get_brands_with_model_count(db_pool)),
            parse_mode=ParseMode.HTML
        )
        await callback_query.answer(f"Моделі для {brand_name} не знайдено.", show_alert=True)


# ОБРОБНИК: Перегляд деталей моделі
@router.callback_query(CatalogCallback.filter(F.action == "select_model"))
async def select_model_handler(
    callback_query: CallbackQuery,
    callback_data: CatalogCallback,
    db_pool: Pool
):
    """
    Обробляє натискання на кнопку моделі, виводить її деталі.
    """
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    model_id = callback_data.model_id
    
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) обрав модель з ID: {model_id}.")

    model_details = await get_model_details_by_id(db_pool, model_id)
    
    if model_details:
        formatted_text = format_model_details(model_details)
        keyboard = get_model_details_keyboard()
        await callback_query.message.edit_text(
            text=formatted_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        await callback_query.answer()
    else:
        await callback_query.answer("Деталі моделі не знайдено.", show_alert=True)


@router.callback_query(CatalogCallback.filter(F.action == "back_to_brands"))
async def back_to_brands_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє натискання кнопки "Назад" до списку брендів.
    """
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) повернувся до списку брендів.")
    
    brands = await get_brands_with_model_count(db_pool)
    
    if brands:
        keyboard = get_brands_inline_keyboard(brands)
        await callback_query.message.edit_text(
            text="<b>Бренди кондиціонерів:</b>\nОберіть бренд для перегляду моделей.",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await callback_query.answer("На жаль, бренди не знайдено.")

    await callback_query.answer()