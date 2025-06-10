# handlers/menu_handler.py
import logging
import math

from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import asyncpg

from keyboards.reply_keyboard import get_main_menu_keyboard, get_main_menu_pages_info
from keyboards.admin_keyboard import get_admin_main_keyboard
from database.users_db import get_user_access_level
# Оновлюємо імпорти, щоб включити нові константи
from common.messages import (
    get_access_level_description,
    get_random_admin_welcome_message,
    HELP_MESSAGE_TEXT, # Додано
    INFO_MESSAGE_TEXT, # Додано
    FIND_MESSAGE_TEXT  # Додано
)
from common.constants import BUTTONS_PER_PAGE, ALL_MENU_BUTTONS, ACCESS_LEVEL_BUTTONS

from common.states import AdminStates, MenuStates

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "⬅️ Назад", MenuStates.main_menu)
@router.message(F.text == "➡️ Іще", MenuStates.main_menu)
@router.message(F.text == "На головну", MenuStates.any)
async def show_main_menu_handler(
    message: types.Message,
    bot: Bot,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    is_pagination_action_forward = message.text == "➡️ Іще"
    is_pagination_action_backward = message.text == "⬅️ Назад"
    is_main_menu_return = message.text == "На головну"
    is_initial_menu_entry = not (is_pagination_action_forward or is_pagination_action_backward or is_main_menu_return)

    logger.info(f"Користувач {user_name} (ID: {user_id}) викликав show_main_menu_handler (дія: {message.text}).")

    if not db_pool:
        logger.error("db_pool не знайдено в аргументах show_main_menu_handler!")
        await message.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    access_level = await get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0
    logger.info(f"Користувач {user_name} (ID: {user_id}) має рівень доступу: {access_level}.")

    current_state_data = await state.get_data()
    current_page = current_state_data.get("menu_page", 0)

    total_buttons, total_pages = get_main_menu_pages_info(access_level)

    if is_pagination_action_backward:
        current_page = max(0, current_page - 1)
    elif is_pagination_action_forward:
        current_page = min(total_pages - 1, current_page + 1)
    elif is_main_menu_return:
        current_page = 0
        await state.set_state(MenuStates.main_menu)

    await state.update_data(menu_page=current_page)
    
    menu_message_text = ""
    if is_main_menu_return or is_initial_menu_entry:
        level_name, level_description = get_access_level_description(access_level, ACCESS_LEVEL_BUTTONS)
        menu_message_text = (
            "Ваш рівень доступу:\n"
            f"<b>{level_name}</b>\n"
            f"{level_description}"
        )
    elif is_pagination_action_forward:
        menu_message_text = "Ви перейшли до наступної сторінки меню."
    elif is_pagination_action_backward:
        menu_message_text = "Ви повернулись до попередньої сторінки меню."
    
    keyboard = await get_main_menu_keyboard(access_level, current_page)
    await message.answer(menu_message_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)


@router.message(F.text == "⚙️ Адміністрування", MenuStates.main_menu)
async def handle_admin_button(
    message: types.Message,
    bot: Bot,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    logger.info(f"Користувач {user_name} (ID: {user_id}) натиснув кнопку '⚙️ Адміністрування'.")

    if not db_pool:
        logger.error("db_pool не знайдено в аргументах handle_admin_button!")
        await message.answer("Виникла внутрішня помилка. Будь ласка, спробуйте пізніше.")
        return

    access_level = await get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0
    
    if access_level >= 10:
        admin_keyboard = get_admin_main_keyboard()
        
        welcome_admin_text = get_random_admin_welcome_message()
        await state.set_state(AdminStates.admin_main)
        
        await message.answer(
            f"{welcome_admin_text}",
            reply_markup=admin_keyboard,
            parse_mode=ParseMode.HTML
        )
        logger.info(f"Користувачу {user_id} (рівень {access_level}) відображено панель адміністратора.")
    else:
        await message.answer(
            "У вас немає доступу до панелі адміністратора.",
            reply_markup=await get_main_menu_keyboard(access_level, 0)
        )
        logger.warning(f"Користувач {user_id} (рівень {access_level}) спробував отримати доступ до адмін-панелі без дозволу.")

@router.message(Command("help"))
async def command_help_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) виконав команду /help.")
    # Використовуємо константу
    await message.answer(HELP_MESSAGE_TEXT, parse_mode=ParseMode.HTML)

@router.message(Command("info"))
async def command_info_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) виконав команду /info.")
    # Використовуємо константу
    await message.answer(INFO_MESSAGE_TEXT, parse_mode=ParseMode.HTML)

@router.message(Command("find"))
async def command_find_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) виконав команду /find.")
    # Використовуємо константу
    await message.answer(FIND_MESSAGE_TEXT, parse_mode=ParseMode.HTML)