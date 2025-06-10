# handlers/admin/main_menu.py
import logging
import math # Для math.ceil у process_show_users

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter

import asyncpg

from keyboards.admin_keyboard import get_admin_main_keyboard, get_users_list_keyboard, get_telethon_actions_keyboard
from keyboards.reply_keyboard import get_main_menu_keyboard # Для повернення в головне меню
from database.users_db import get_user_access_level, get_all_users
from common.messages import get_access_level_description
from common.constants import USERS_PER_PAGE, ACCESS_LEVEL_BUTTONS # Додано ACCESS_LEVEL_BUTTONS

# Імпортуємо стани з централізованого файлу
from common.states import AdminStates, MenuStates
from filters.admin_filter import AdminAccessFilter # Для застосування до роутера або хендлерів
from keyboards.callback_factories import AdminCallback, UserActionCallback, AccessLevelCallback

logger = logging.getLogger(__name__)

router = Router()

# Застосовуємо фільтр адмін-доступу до всього роутера
# Це гарантує, що тільки адміністратори зможуть викликати хендлери в цьому роутері.
router.callback_query.filter(AdminAccessFilter())
router.message.filter(AdminAccessFilter())


# Хендлер для повернення в головне адмін-меню
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.admin_main)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.user_management)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.confirm_action)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.set_access_level)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.telethon_management)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.waiting_for_telethon_input)
@router.callback_query(AdminCallback.filter(F.action == "cancel_admin_action"), AdminStates.chat_matrix_management) # ВИПРАВЛЕНО: Додано стан для Чат-матриці
async def back_to_admin_main_menu(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    logger.info(f"Користувач {callback.from_user.id} натиснув '⬅️ Назад до адмін-меню'.")
    await state.set_state(AdminStates.admin_main)
    keyboard = get_admin_main_keyboard()
    await callback.message.edit_text(
        "<b>Адмін-панель:</b>\n\nОберіть дію:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


# Хендлер для кнопки "🏁 Завершити командування"
@router.callback_query(AdminCallback.filter(F.action == "close_admin_panel"), AdminStates.admin_main)
async def close_admin_panel(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool # db_pool потрібен для отримання рівня доступу
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув '🏁 Завершити командування'.")

    await state.set_state(MenuStates.main_menu)
    
    access_level = await get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0
    
    current_state_data = await state.get_data()
    current_page = current_state_data.get("menu_page", 0) # Повертаємось на ту ж сторінку меню, що була

    keyboard = await get_main_menu_keyboard(access_level, current_page)
    
    level_name, level_description = get_access_level_description(access_level, ACCESS_LEVEL_BUTTONS)

    await callback.message.delete() # Видаляємо попереднє повідомлення з inline-клавіатурою
    await callback.message.answer( # Відправляємо нове повідомлення з ReplyKeyboardMarkup
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
            "<b>👥 Юзер-матриця · Редактор доступу:</b>\n\nНемає зареєстрованих користувачів.",
            reply_markup=get_admin_main_keyboard(), # Повертаємось до головного адмін-меню
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

# Хендлер для кнопки "📡 ReLink · Статус каналу зв'язку"
# !!! ЦЕЙ ХЕНДЛЕР МАЄ БУТИ ВИДАЛЕНИЙ ПІСЛЯ УСПІШНОГО ЗАПУСКУ БОТА З ОНОВЛЕНОЮ СТРУКТУРОЮ.
# !!! ВІН ТИМЧАСОВО ДУБЛЮЄТЬСЯ В telethon_operations.py
# !!! Я ЗАЛИШИВ ЙОГО ТУТ ДЛЯ ПОТОЧНОЇ ПЕРЕВІРКИ, АЛЕ ВІН ЗАЙВИЙ.
# !!! ЛОГІКА ДЛЯ ЦІЄЇ КНОПКИ ПОВИННА ОБРОБЛЯТИСЯ В telethon_operations.py
# @router.callback_query(
#      AdminCallback.filter(F.action == "connection_status"), # Це callback для кнопки "📡 ReLink · Статус каналу зв'язку"
#      StateFilter(AdminStates.admin_main, AdminStates.telethon_management)
# )
# async def telethon_connection_status(
#      callback: types.CallbackQuery,
#      telethon_manager: Any # telethon_manager має бути переданий через Middleware
# ) -> None:
#      user_id = callback.from_user.id
#      logger.info(f"Користувач {user_id} перевіряє статус з'єднання.")
#      logger.debug(f"Telethon Manager received in telethon_connection_status: {telethon_manager}")
    
#      status_message = "❌ Telethon API: не підключено або немає активних клієнтів."

#      if telethon_manager and telethon_manager.clients:
#          for phone_number, client_obj in telethon_manager.clients.items():
#              if client_obj.is_connected():
#                  status_message = f"✅ Telethon API: підключено (через {phone_number})"
#                  break
    
#      await callback.answer(status_message, show_alert=True)