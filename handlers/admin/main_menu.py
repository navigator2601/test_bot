# handlers/admin/main_menu.py

import logging
import math
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter

import asyncpg

from keyboards.admin_keyboard import get_admin_main_keyboard, get_telethon_actions_keyboard, get_chat_matrix_keyboard
from keyboards.reply_keyboard import get_main_menu_keyboard
from database.users_db import get_user_access_level
from common.messages import get_access_level_description, get_random_admin_welcome_message
from common.constants import ACCESS_LEVEL_BUTTONS

from common.states import AdminStates, MenuStates
from filters.admin_filter import AdminAccessFilter
from keyboards.callback_factories import AdminCallback

logger = logging.getLogger(__name__)

router = Router()

router.callback_query.filter(AdminAccessFilter())
router.message.filter(AdminAccessFilter())

# Хендлер для повернення в головне адмін-меню
# Цей хендлер викликається, коли адміністратор натискає "⬅️ Назад до адмін-меню" з підменю
# Тепер використовуємо ОДИН StateFilter для всіх відповідних станів
@router.callback_query(
    AdminCallback.filter(F.action == "cancel_admin_action"),
    StateFilter(
        AdminStates.admin_main,
        AdminStates.user_management,
        AdminStates.confirm_action,
        AdminStates.set_access_level,
        AdminStates.telethon_management,
        AdminStates.waiting_for_telethon_input,
        AdminStates.chat_matrix_management
    )
)
async def back_to_admin_main_menu(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    logger.info(f"Користувач {callback.from_user.id} натиснув '⬅️ Назад до адмін-меню'.")
    await state.set_state(AdminStates.admin_main) # Встановлюємо стан назад до головного адмін-меню
    keyboard = get_admin_main_keyboard()
    
    welcome_message = get_random_admin_welcome_message()
    
    await callback.message.edit_text(
        welcome_message,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# Хендлер для кнопки "🏁 Завершити командування"
# Цей хендлер вже використовує єдиний StateFilter з попередніх виправлень
@router.callback_query(
    AdminCallback.filter(F.action == "close_admin_panel"),
    StateFilter(
        AdminStates.admin_main,
        AdminStates.user_management,
        AdminStates.telethon_management,
        AdminStates.chat_matrix_management,
        AdminStates.set_access_level,
        AdminStates.confirm_action,
        AdminStates.waiting_for_telethon_input
    )
)
async def close_admin_panel(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув '🏁 Завершити командування'.")

    await state.clear()
    await state.set_state(MenuStates.main_menu)
    
    access_level = await get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0
    
    # Після clear() current_state_data буде пустий, тому .get() з дефолтом
    current_state_data = await state.get_data()
    current_page = current_state_data.get("menu_page", 0)

    keyboard = await get_main_menu_keyboard(access_level, current_page)
    
    level_name, level_description = get_access_level_description(access_level, ACCESS_LEVEL_BUTTONS)

    await callback.message.delete()
    await callback.message.answer(
        f"Ви повернулися до головного меню.\n\nВаш рівень доступу:\n<b>{level_name}</b>\n{level_description}",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# ... (решта коду без змін) ...