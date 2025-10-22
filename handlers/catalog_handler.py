# відносний шлях до файлу: handlers/catalog_handler.py
# Призначення: Обробка запитів, пов'язаних з каталогом кондиціонерів.

import logging
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from asyncpg import Pool
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

from database.db_search_functions import get_all_brands_with_count, get_models_by_brand, get_model_details_by_id
from database.users_db import get_user_access_level
from keyboards.inline_keyboard import get_brands_inline_keyboard, get_models_inline_keyboard, get_model_details_menu_keyboard, get_back_to_models_keyboard
from keyboards.reply_keyboard import get_main_menu_keyboard
from services.message_formatter import (
    format_model_details_message,
    format_description,
    format_general_characteristics,
    format_technical_parameters,
    format_installation_parameters,
    format_functions
)

router = Router()
logger = logging.getLogger(__name__)

CATALOG_ACTIVATED_MESSAGE = "⚡ Каталог активовано! \nКристали даних виявили бренди:"

class ModelDetailsStates(StatesGroup):
    """
    Стан для зберігання деталей моделі, щоб уникнути повторних запитів до БД.
    """
    viewing_details = State()

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

@router.callback_query(F.data == "back_to_brands")
async def back_to_brands_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє натискання кнопки "Назад до брендів".
    Повертає користувача до списку брендів.
    """
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) повернувся до списку брендів.")

    brands = await get_all_brands_with_count(db_pool)
    keyboard = await get_brands_inline_keyboard(brands)
    
    await callback_query.message.edit_text(
        CATALOG_ACTIVATED_MESSAGE,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
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
            f"✅ Ось список моделей для бренду <b>{brand_name}</b>:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await callback_query.message.edit_text("❌ На жаль, моделі для цього бренду не знайдено.")

    await callback_query.answer()

@router.callback_query(F.data.startswith("model_details_"))
async def show_specific_model_details_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє натискання на кнопки "Опис", "Характеристики" тощо.
    Виводить відповідні дані, не прибираючи клавіатуру деталей.
    """
    try:
        parts = callback_query.data.split("_")
        detail_type = parts[2]
        model_id = int(parts[3])
    except (IndexError, ValueError):
        logger.error(f"Некоректний формат callback_data: {callback_query.data}")
        await callback_query.message.edit_text(
            "❌ Виникла помилка при обробці запиту.",
            reply_markup=callback_query.message.reply_markup,
            parse_mode=ParseMode.HTML
        )
        await callback_query.answer()
        return

    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) обрав перегляд '{detail_type}' для моделі з ID: {model_id}.")
    
    model_data = await get_model_details_by_id(db_pool, model_id)

    if not model_data:
        await callback_query.message.edit_text(
            "❌ Деталі моделі не знайдено.",
            reply_markup=callback_query.message.reply_markup,
            parse_mode=ParseMode.HTML
        )
        await callback_query.answer()
        return

    formatted_message = ""

    if detail_type == "desc":
        formatted_message = format_description(model_data)
    elif detail_type == "general":
        formatted_message = format_general_characteristics(model_data)
    elif detail_type == "functions":
        formatted_message = format_functions(model_data)
    elif detail_type == "technical":
        formatted_message = format_technical_parameters(model_data)
    elif detail_type == "installation":
        formatted_message = format_installation_parameters(model_data)
    else:
        formatted_message = "❌ Невідомий тип деталізації."
        
    if not formatted_message:
        formatted_message = "❌ На жаль, дані для цієї категорії відсутні."
    
    await callback_query.message.edit_text(
        formatted_message,
        reply_markup=callback_query.message.reply_markup,
        parse_mode=ParseMode.HTML
    )

    await callback_query.answer()


@router.callback_query(F.data.startswith("model_"))
async def show_model_details_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє вибір моделі та показує меню її деталей.
    """
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

    keyboard = await get_model_details_menu_keyboard(model_id, brand_name_from_callback)

    await callback_query.message.edit_text(
        "⚙️ Оберіть опцію для перегляду деталей моделі:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

    await callback_query.answer()

@router.callback_query(F.data.startswith("back_to_models_"))
async def back_to_models_handler(callback_query: CallbackQuery, db_pool: Pool):
    """
    Обробляє натискання кнопки "Назад до моделей".
    """
    try:
        brand_name = callback_query.data.split("_")[3]
    except IndexError:
        await callback_query.answer("❌ Виникла помилка при обробці запиту. Повертаю до брендів.", show_alert=True)
        await back_to_brands_handler(callback_query, db_pool)
        return

    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) повернувся до списку моделей для бренду '{brand_name}'.")

    models = await get_models_by_brand(db_pool, brand_name)

    if models:
        keyboard = await get_models_inline_keyboard(models)
        await callback_query.message.edit_text(
            f"✅ Ось список моделей для бренду <b>{brand_name}</b>:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await callback_query.message.edit_text("❌ На жаль, моделі для цього бренду не знайдено.")

    await callback_query.answer()