# Файл: handlers/admin/db_operations.py

import logging
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove # Додано ReplyKeyboardRemove
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter # 🔥 ВИПРАВЛЕНО: Додано StateFilter
from asyncpg import Pool
from aiogram.exceptions import TelegramBadRequest
from typing import List, Dict, Optional
import random

# ВИЗНАЧЕННЯ ROUTER
router = Router()
logger = logging.getLogger(__name__)

# 🔥 ВИПРАВЛЕНО: Додано необхідні імпорти
from filters.admin_filter import AdminAccessFilter # Якщо ви використовуєте адмін-фільтр
from common.states import DbOperationStates, MenuStates
from database.users_db import get_user_access_level
from keyboards.reply_keyboard import get_main_menu_keyboard

# ІМПОРТ КЛАВІАТУР З keyboards/admin_inline_keyboard.py
from keyboards.admin_inline_keyboard import (
    get_db_operations_start_keyboard,  # 🔥 ВИПРАВЛЕНО: ЦЕЙ ІМПОРТ БУВ ВТРАЧЕНИЙ
    get_db_operations_edit_category_keyboard,
    get_admin_brand_series_selection_keyboard
)

# Застосування адмін-фільтра до всього роутера
# Якщо ви не використовуєте фільтр на цьому рівні, можна прибрати, 
# але це стандартна практика для адмін-роутерів.
router.message.filter(AdminAccessFilter())
router.callback_query.filter(AdminAccessFilter())

# ----------------------------------------------------------------------
# 🔥🔥🔥 ФУНКЦІЯ ОТРИМАННЯ ДАНИХ З БД (ВИКОРИСТОВУЄ ВАШ SQL) 🔥🔥🔥
# ----------------------------------------------------------------------

# Ваш SQL-запит для підрахунку % наповнення
# ... (весь SQL запит залишається без змін) ...
# ...

# --- ОБРОБНИК: Вхід у модуль "Керування БД" (за текстом Reply Keyboard) ---
@router.message(
    F.text == "📝 Додати або редагувати дані",
    StateFilter(MenuStates.main_menu)
)
async def start_db_operations(message: types.Message, state: FSMContext, db_pool: Pool):
    user_id = message.from_user.id
    current_state = await state.get_state()

    logger.info(
        f"Адмін {user_id} у стані {current_state} натиснув '📝 Додати або редагувати дані'. "
        f"Запуск керування БД."
    )

    await state.set_state(DbOperationStates.db_operation_start)

    # 🔥 Рядок, де виникла помилка, тепер працюватиме коректно
    keyboard = get_db_operations_start_keyboard()

    await message.answer(
        "🛠️ **Керування Базою Даних**\n\n"
        "Оберіть операцію для роботи з даними:",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

# ... (решта коду) ...