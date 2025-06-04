# handlers/admin_handler.py

import logging
from aiogram import Router, types, Bot, F
from aiogram.filters import StateFilter  # Для фільтрації декількох станів FSMContext у aiogram 3.x
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
import asyncpg
from typing import Any, Optional

from database import users_db
from keyboards.admin_keyboard import (
    get_admin_main_keyboard,
    get_users_list_keyboard,
    get_user_actions_keyboard,
    get_confirm_action_keyboard,
    get_access_level_keyboard,
    get_telethon_actions_keyboard
)
from keyboards.reply_keyboard import get_main_menu_keyboard
from common.messages import get_access_level_description, get_random_admin_welcome_message
from common.constants import ACCESS_LEVEL_BUTTONS, BUTTONS_PER_PAGE
from keyboards.callback_factories import AdminCallback, UserActionCallback, AccessLevelCallback  # <--- ІМПОРТ callback-фабрик

router = Router()  # router має бути оголошено ДО використання у декораторах

class AdminStates(StatesGroup):
    admin_main = State()
    user_management = State()
    confirm_action = State()
    set_access_level = State()
    telethon_management = State()

# ...залишаєш інші функції без змін...

# УВАГА! Декоратори нижче НЕ мають використовувати оператор | для State!
# Замість цього використовуємо StateFilter

@router.callback_query(
    AdminCallback.filter(F.action == "telethon_auth"),
    StateFilter(AdminStates.admin_main, AdminStates.telethon_management)
)
async def process_telethon_auth(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logging.info(f"Користувач {user_id} натиснув 'TeleKey · Авторизація API-зв’язку'.")
    await state.set_state(AdminStates.telethon_management)
    keyboard = get_telethon_actions_keyboard()
    await callback.message.edit_text(
        "<b>🔐 TeleKey · Авторизація API-зв’язку:</b>\n\nОберіть дію для управління Telethon API:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@router.callback_query(
    F.data == "cancel_admin_action",
    StateFilter(AdminStates.user_management, AdminStates.telethon_management, AdminStates.set_access_level)
)
async def cancel_admin_action(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext,
    bot: Bot
) -> None:
    user_id = callback.from_user.id
    logging.info(f"Користувач {user_id} скасував адмін-дію і повертається до головного адмін-меню.")
    await state.set_state(AdminStates.admin_main)
    await state.update_data(pending_action=None, selected_user_id=None)
    await callback.message.edit_text(
        "Ви повернулись до головної адмін-панелі.",
        reply_markup=get_admin_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@router.callback_query(
    F.data == "close_admin_panel",
    StateFilter(AdminStates)  # <--- ОНОВЛЕНО: реагує на будь-який підстан AdminStates
)
async def close_admin_panel(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logging.info(f"Користувач {user_id} закриває адмін-панель.")
    await state.clear()
    await state.set_state(MenuStates.main_menu)
    access_level = await users_db.get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0

    try:
        await callback.message.edit_text(
            callback.message.text,
            reply_markup=None
        )
    except Exception:
        pass

    await callback.message.answer(
        "Ви вийшли з адмін-панелі. Повернення до головного меню.",
        reply_markup=await get_main_menu_keyboard(access_level, 0),
        parse_mode=ParseMode.HTML
    )
    await callback.answer("Адмін-панель закрито.")
    logging.info(f"Адмін-панель закрито для користувача {user_id}.")

# ...і так далі для інших хендлерів...

# КОМЕНТАР:
# 1. router = Router() має бути до всіх декораторів.
# 2. Для декількох станів використовуй лише StateFilter.
# 3. Твоя логіка й решта коду залишаються незмінними, лише виправлено порядок і синтаксис для сумісності з aiogram 3.x.