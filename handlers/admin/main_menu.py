# handlers/admin/main_menu.py

import logging
import math
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter

import asyncpg

from keyboards.admin_keyboard import get_admin_main_keyboard, get_users_list_keyboard, get_telethon_actions_keyboard
from keyboards.reply_keyboard import get_main_menu_keyboard
from database.users_db import get_user_access_level, get_all_users
from common.messages import get_access_level_description, get_random_admin_welcome_message # <--- Додано імпорт
from common.constants import USERS_PER_PAGE, ACCESS_LEVEL_BUTTONS

from common.states import AdminStates, MenuStates
from filters.admin_filter import AdminAccessFilter
from keyboards.callback_factories import AdminCallback, UserActionCallback, AccessLevelCallback

logger = logging.getLogger(__name__)

router = Router()

router.callback_query.filter(AdminAccessFilter())
router.message.filter(AdminAccessFilter())


# Хендлер для повернення в головне адмін-меню
# Цей хендлер викликається, коли адміністратор натискає "⬅️ Назад до адмін-меню" з підменю
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.admin_main)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.user_management)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.confirm_action)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.set_access_level)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.telethon_management)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.waiting_for_telethon_input)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.chat_matrix_management)
async def back_to_admin_main_menu(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    logger.info(f"Користувач {callback.from_user.id} натиснув '⬅️ Назад до адмін-меню'.")
    await state.set_state(AdminStates.admin_main)
    keyboard = get_admin_main_keyboard()
    
    # <--- ЗМІНЕНО ТУТ: Використовуємо рандомне повідомлення
    welcome_message = get_random_admin_welcome_message()
    
    await callback.message.edit_text(
        welcome_message, # <--- Рандомне повідомлення
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


# Хендлер для кнопки "🏁 Завершити командування"
@router.callback_query(AdminCallback.filter(F.action == "close_admin_panel"), AdminStates.admin_main)
async def close_admin_panel(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув '🏁 Завершити командування'.")

    await state.set_state(MenuStates.main_menu)
    
    access_level = await get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0
    
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

# Хендлер для кнопки "👥 Юзер-матриця · Редактор доступу"
@router.callback_query(
    AdminCallback.filter(F.action == "show_users"),
    StateFilter(AdminStates.admin_main, AdminStates.user_management)
)
async def process_show_users(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool,
    callback_data: AdminCallback
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув 'Юзер-матриця'.")

    await state.set_state(AdminStates.user_management)
    
    current_page = callback_data.page if callback_data.page is not None else 0
    await state.update_data(users_list_page=current_page)

    users = await get_all_users(db_pool)
    if not users:
        await callback.answer("Не знайдено жодного користувача в базі даних.", show_alert=True)
        await callback.message.edit_text(
            f"{get_random_admin_welcome_message()}\n\n" # <--- Можливо, тут теж варто використати рандомне
            "<b>👥 Юзер-матриця · Редактор доступу:</b>\n\nНемає зареєстрованих користувачів.",
            reply_markup=get_admin_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    keyboard = get_users_list_keyboard(users, current_page, USERS_PER_PAGE)
    
    total_pages = math.ceil(len(users) / USERS_PER_PAGE) if len(users) > 0 else 1
    
    message_text = (
        f"<b>👥 Юзер-матриця · Редактор доступу:</b>\n\n"
        f"Оберіть користувача для редагування доступу ({current_page + 1}/{total_pages}):"
    )
    
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# --- Хендлер для кнопки "🔐 TeleKey · Авторизація API-зв’язку" ---
@router.callback_query(AdminCallback.filter(F.action == "telethon_auth"), AdminStates.admin_main)
async def process_telethon_auth_button(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув '🔐 TeleKey · Авторизація API-зв’язку'.")
    
    # Переходимо в стан управління Telethon
    await state.set_state(AdminStates.telethon_management)
    
    # Відправляємо повідомлення з опціями для Telethon
    keyboard = get_telethon_actions_keyboard()
    await callback.message.edit_text(
        "<b>🔐 TeleKey · Панель керування API-зв’язком:</b>\n\nОберіть дію:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


# Хендлер для кнопки "💬 Чат-матриця · Перегляд активних зон"
@router.callback_query(AdminCallback.filter(F.action == "chat_matrix"), AdminStates.admin_main)
async def process_chat_matrix_button(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув '💬 Чат-матриця'.")
    
    await state.set_state(AdminStates.chat_matrix_management)
    
    keyboard = get_chat_matrix_keyboard() # Потрібно імпортувати get_chat_matrix_keyboard
    await callback.message.edit_text(
        "<b>💬 Чат-матриця · Перегляд активних зон:</b>\n\nОберіть дію:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()