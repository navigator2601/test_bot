# Файл: handlers/catalog_handler.py
# Призначення: Обробник для функціоналу "Каталог".
# Обробляє запит на відкриття каталогу і виводить список брендів.

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from asyncpg import Pool
from aiogram.utils.markdown import hbold, hcode
from aiogram.fsm.context import FSMContext
from common.states import CatalogStates

# Імпортуємо всі наші функції для роботи з БД
from database.db_search_functions import (
    get_brands_with_model_count, 
    get_models_by_brand, 
    get_model_details_by_name,
    format_full_info,
    format_general_info,
    format_tech_info,
    format_functions_info
)

# Імпортуємо всі функції для клавіатур
from keyboards.inline_keyboard import (
    get_brands_inline_keyboard, 
    get_models_inline_keyboard, 
    get_model_info_keyboard
)

router = Router()
logger = logging.getLogger(__name__)

# Обробник для кнопки "Каталог"
@router.message(F.text == "📚 Каталог")
async def show_catalog_handler(message: Message, db_pool: Pool):
    user_id = message.from_user.id
    user_fullname = message.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) натиснув кнопку '📚 Каталог'.")
    
    brands = await get_brands_with_model_count(db_pool)
    
    if brands:
        logger.info(f"Знайдено {len(brands)} брендів у БД. Формую inline-клавіатуру.")
        keyboard = await get_brands_inline_keyboard(brands)
        await message.answer("📁 **Каталог брендів:**", reply_markup=keyboard)
        logger.info(f"Відправлено каталог брендів користувачу {user_id}.")
    else:
        logger.warning(f"Увага: У базі даних не знайдено жодного бренду. Відправляю відповідь користувачу {user_id}.")
        await message.answer("На жаль, в базі даних немає доступних брендів.")


# Обробник для вибору бренду
@router.callback_query(F.data.startswith("brand_"))
async def select_brand_handler(callback_query: CallbackQuery, db_pool: Pool):
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    brand_name = callback_query.data.split('_')[1]
    
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) вибрав бренд '{brand_name}'.")
    
    models = await get_models_by_brand(db_pool, brand_name)
    
    if models:
        logger.info(f"Знайдено {len(models)} моделей для бренду '{brand_name}'. Формую inline-клавіатуру.")
        keyboard = await get_models_inline_keyboard(models)
        await callback_query.message.edit_text(
            text=f"📦 **Моделі {brand_name}:**",
            reply_markup=keyboard
        )
        logger.info(f"Відредаговано повідомлення для користувача {user_id}, показано моделі.")
    else:
        logger.warning(f"Увага: Не знайдено жодної моделі для бренду '{brand_name}'.")
        await callback_query.message.edit_text(
            text=f"❌ **Моделі {brand_name}:**\nНа жаль, моделі для цього бренду не знайдено.",
            reply_markup=None
        )
    await callback_query.answer()


# Обробник для вибору моделі (зберігає дані в стані FSM)
@router.callback_query(F.data.startswith("model_details_"))
async def select_model_handler(callback_query: CallbackQuery, db_pool: Pool, state: FSMContext):
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    model_name = callback_query.data.split('_details_')[1]
    
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) вибрав модель '{model_name}'.")

    model_data = await get_model_details_by_name(db_pool, model_name)
    
    if not model_data:
        logger.warning(f"Увага: Не знайдено деталей для моделі '{model_name}'.")
        await callback_query.message.edit_text(
            text=f"❌ **Деталі моделі '{model_name}':**\nІнформацію не знайдено.",
            reply_markup=None
        )
        await state.clear()
        await callback_query.answer()
        return

    brand_name = model_name.split(' ')[0]
    
    await state.set_state(CatalogStates.viewing_model_info)
    await state.update_data(model_info=model_data, brand_name=brand_name)
    
    keyboard = await get_model_info_keyboard(model_name, brand_name)
    await callback_query.message.edit_text(
        text=f"🔎 **Інформація про модель {model_name}**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    logger.info(f"Відредаговано повідомлення, показано клавіатуру категорій для моделі '{model_name}'.")
    await callback_query.answer()


# Обробник для кнопок з категоріями інформації (використовує дані зі стану)
@router.callback_query(F.data.startswith("info_"), CatalogStates.viewing_model_info)
async def show_model_info_handler(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name

    parts = callback_query.data.split('_', 2)
    info_type = parts[1]
    model_name = parts[2]
    
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) запросив '{info_type}' інформацію для моделі '{model_name}'.")

    user_data = await state.get_data()
    model_data = user_data.get('model_info')
    brand_name = user_data.get('brand_name')

    formatted_text = ""
    if not model_data:
        formatted_text = f"❌ Дані для моделі `{model_name}` не знайдено у стані. Будь ласка, спробуйте знову."
    else:
        if info_type == 'general':
            formatted_text = format_general_info(model_data)
        elif info_type == 'tech':
            formatted_text = format_tech_info(model_data)
        elif info_type == 'functions':
            formatted_text = format_functions_info(model_data)
        elif info_type == 'full':
            formatted_text = format_full_info(model_data)
            
    keyboard = await get_model_info_keyboard(model_name, brand_name)
    
    await callback_query.message.edit_text(
        text=formatted_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    logger.info(f"Відредаговано повідомлення, показано '{info_type}' інформацію для '{model_name}'.")
    await callback_query.answer()


# Обробник для кнопки "До списку брендів"
@router.callback_query(F.data == "back_to_brands")
async def back_to_brands_handler(callback_query: CallbackQuery, db_pool: Pool, state: FSMContext):
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) повернувся до списку брендів.")
    
    await state.clear()

    brands = await get_brands_with_model_count(db_pool)
    
    keyboard = await get_brands_inline_keyboard(brands)
    await callback_query.message.edit_text(
        text="📁 **Каталог брендів:**",
        reply_markup=keyboard
    )
    logger.info(f"Відредаговано повідомлення для користувача {user_id}, показано список брендів.")
    
    await callback_query.answer()


# Обробник для кнопки "До списку моделей" (виходить зі стану)
@router.callback_query(F.data.startswith("back_to_models_"), CatalogStates.viewing_model_info)
async def back_to_models_handler(callback_query: CallbackQuery, db_pool: Pool, state: FSMContext):
    user_id = callback_query.from_user.id
    user_fullname = callback_query.from_user.full_name
    brand_name = callback_query.data.split('_')[3]
    logger.info(f"Користувач {user_fullname} (ID: {user_id}) повернувся до списку моделей бренду '{brand_name}'.")

    models = await get_models_by_brand(db_pool, brand_name)
    
    keyboard = await get_models_inline_keyboard(models)
    await callback_query.message.edit_text(
        text=f"📦 **Моделі {brand_name}:**",
        reply_markup=keyboard
    )
    logger.info(f"Відредаговано повідомлення для користувача {user_id}, показано список моделей.")
    
    await state.clear()
    
    await callback_query.answer()