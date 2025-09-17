# відносний шлях до файлу: handlers/catalog_handler.py
# Призначення: Обробка запитів, пов'язаних з каталогом кондиціонерів.

import logging
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from asyncpg import Pool
from aiogram.fsm.context import FSMContext
import re

from database.db_search_functions import get_all_brands_with_count, get_models_by_brand, get_model_details_by_id
from database.users_db import get_user_access_level
from keyboards.inline_keyboard import get_brands_inline_keyboard, get_models_inline_keyboard, get_back_to_models_keyboard
from keyboards.reply_keyboard import get_main_menu_keyboard
from services.message_formatter import format_model_details_message

router = Router()
logger = logging.getLogger(__name__)

CATALOG_ACTIVATED_MESSAGE = "⚡ Каталог активовано! \\nКристали даних виявили бренди:"

@router.message(F.text == "📚 Каталог")
async def show_catalog_handler_message(message: Message, db_pool: Pool):
    """
    Обробляє натискання кнопки '📚 Каталог'.
    Відправляє тимчасове повідомлення для приховування реплі-клавіатури,
    видаляє його і відправляє нове з інлайн-клавіатурою брендів.
    """
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) натиснув кнопку '📚 Каталог'.")
    
    # Відправляємо тимчасове повідомлення, щоб приховати реплі-клавіатуру
    sent_temp_message = await message.answer(
        "Завантаження...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    try:
        await sent_temp_message.delete()
        logger.info(f"Видалено тимчасове повідомлення для приховування клавіатури.")
    except Exception as e:
        logger.error(f"Помилка при видаленні тимчасового повідомлення: {e}")

    brands = await get_all_brands_with_count(db_pool)
    
    if brands:
        keyboard = await get_brands_inline_keyboard(brands)
        await message.answer(
            CATALOG_ACTIVATED_MESSAGE,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer(
            "❌ На жаль, бренди не знайдено."
        )

@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє натискання кнопки "В головне меню".
    Видаляє повідомлення з інлайн-клавіатурою і показує головне меню.
    """
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) повернувся в головне меню.")
    
    await callback_query.message.delete()
    
    user_access_level = await get_user_access_level(db_pool, user_id)
    main_menu_keyboard = await get_main_menu_keyboard(user_access_level)
    
    await callback_query.message.answer(
        "👋 Ласкаво просимо до головного меню!",
        reply_markup=main_menu_keyboard
    )
    await callback_query.answer()

@router.callback_query(F.data.startswith("brand_"))
async def show_models_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє вибір бренду та показує список моделей.
    """
    brand_name = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) вибрав бренд '{brand_name}'.")

    models = await get_models_by_brand(db_pool, brand_name)

    if models:
        keyboard = await get_models_inline_keyboard(models)
        await callback_query.message.edit_text(
            f"✅ Ось список моделей для бренду **{brand_name}**:",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await callback_query.message.edit_text("❌ На жаль, моделі для цього бренду не знайдено.")

    await callback_query.answer()

@router.callback_query(F.data.startswith("model_"))
async def show_model_details_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє вибір моделі та показує її деталі.
    """
    await callback_query.message.edit_text("Завантаження деталей моделі...")

    try:
        parts = callback_query.data.split("_")
        brand_name_from_callback = parts[1]
        model_id = int(parts[2])
    except (IndexError, ValueError):
        logger.error(f"Некоректний формат callback_data: {callback_query.data}")
        await callback_query.message.edit_text("❌ Виникла помилка при обробці запиту.")
        await callback_query.answer()
        return
        
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) обрав модель з ID: {model_id}.")

    model_data = await get_model_details_by_id(db_pool, model_id)
    
    if model_data:
        # Виправлення: прибираємо `await`, оскільки функція синхронна
        formatted_message = format_model_details_message(model_data)
        
        keyboard = await get_back_to_models_keyboard(brand_name_from_callback)
        
        await callback_query.message.edit_text(
            formatted_message,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await callback_query.message.edit_text("❌ Деталі моделі не знайдено.")
        
    await callback_query.answer()