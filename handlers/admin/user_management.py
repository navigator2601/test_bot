# handlers/admin/user_management.py
import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter

import asyncpg

from database.users_db import (
    get_user,
    update_user_access_level,
    get_all_users,
    is_user_authorized,
    update_user_authorization_status
)
from keyboards.admin_keyboard import (
    get_users_list_keyboard,
    get_user_actions_keyboard,
    get_confirm_action_keyboard,
    get_access_level_keyboard,
    get_admin_main_keyboard # Додано імпорт для обробки помилок
)
from common.constants import USERS_PER_PAGE, ACCESS_LEVEL_BUTTONS
from common.messages import (
    get_access_level_description,
    get_user_details_text
)

from common.states import AdminStates
from filters.admin_filter import AdminAccessFilter
from keyboards.callback_factories import AdminCallback, UserActionCallback, AccessLevelCallback

logger = logging.getLogger(__name__)

router = Router()

router.callback_query.filter(AdminAccessFilter())
router.message.filter(AdminAccessFilter())


# --- ДОПОМІЖНІ ФУНКЦІЇ ---

async def _return_to_user_management(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool,
    user_id: int
) -> None:
    """
    Повертає бота до відображення інформації про конкретного користувача та його меню дій.
    """
    await state.set_state(AdminStates.user_management)

    user_info = await get_user(db_pool, user_id)
    if user_info:
        is_auth = await is_user_authorized(db_pool, user_id)
        current_level = user_info.get('access_level', 0)
        
        user_info_text = get_user_details_text(user_info, is_auth, ACCESS_LEVEL_BUTTONS)
        keyboard = get_user_actions_keyboard(is_auth, current_level, user_id)
        
        await callback.message.edit_text(user_info_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        # Якщо користувача раптом не знайдено, повертаємо до списку користувачів
        logger.warning(f"Користувач {user_id} не знайдений для повернення в user_management. Повернення до списку.")
        users = await get_all_users(db_pool)
        current_page = (await state.get_data()).get("users_list_page", 0)
        keyboard = get_users_list_keyboard(users, current_page, USERS_PER_PAGE)
        await callback.message.edit_text(
            f"Користувача <code>{user_id}</code> не знайдено. Повернення до списку користувачів:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


async def _show_users_list_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool,
    current_page: int = 0
):
    """
    Відображає список користувачів з пагінацією.
    """
    users = await get_all_users(db_pool)
    keyboard = get_users_list_keyboard(users, current_page, USERS_PER_PAGE)
    
    # Визначення загальної кількості сторінок для відображення в повідомленні
    total_pages = (len(users) + USERS_PER_PAGE - 1) // USERS_PER_PAGE if len(users) > 0 else 1
    
    await callback.message.edit_text(
        f"<b>👥 Юзер-матриця · Редактор доступу:</b>\n\nОберіть користувача для редагування доступу ({current_page + 1}/{total_pages}):",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# --- ОСНОВНІ ХЕНДЛЕРИ ---

# Хендлер для відображення списку користувачів
# Тепер обробляє як перший вхід, так і повернення зі сторінки користувача/пагінації
@router.callback_query(
    AdminCallback.filter(F.action == "show_users"),
    StateFilter(AdminStates.admin_main, AdminStates.user_management) # Включено user_management
)
async def process_show_users(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool,
    callback_data: AdminCallback
) -> None:
    user_id_requester = callback.from_user.id
    logger.info(f"Користувач {user_id_requester} обрав 'Юзер-матриця' або 'Назад до списку користувачів'.")

    # Якщо callback_data.page присутній, використовуємо його. Інакше спробуємо взяти зі стану.
    current_page = callback_data.page if callback_data.page is not None else 0
    
    if current_page == 0: # Якщо сторінка не вказана явно в callback_data, спробуємо отримати її з попереднього стану
        state_data = await state.get_data()
        current_page = state_data.get("users_list_page", 0)
        logger.debug(f"Відновлено сторінку: {current_page} зі стану для користувача {user_id_requester}.")
        
    await state.update_data(users_list_page=current_page) # Зберігаємо поточну сторінку
    await state.set_state(AdminStates.user_management)

    try:
        users = await get_all_users(db_pool)
        if not users:
            logger.warning(f"Не знайдено жодного користувача в БД для відображення юзер-матриці. Користувач {user_id_requester}.")
            await callback.answer("Не знайдено жодного користувача в базі даних.", show_alert=True)
            await callback.message.edit_text(
                "<b>👥 Юзер-матриця · Редактор доступу:</b>\n\nНемає зареєстрованих користувачів.",
                reply_markup=get_admin_main_keyboard(), # Повертаємо до головного адмін-меню
                parse_mode=ParseMode.HTML
            )
            return

        await _show_users_list_handler(callback, state, db_pool, current_page)

    except Exception as e:
        logger.error(f"Помилка при відображенні списку користувачів для {user_id_requester}: {e}", exc_info=True)
        await callback.message.edit_text(
            "Виникла помилка при завантаженні списку користувачів. Будь ласка, спробуйте пізніше.",
            reply_markup=get_admin_main_keyboard(), # На випадок помилки повертаємо до головного меню
            parse_mode=ParseMode.HTML
        )
        await callback.answer("Помилка завантаження користувачів.", show_alert=True)


# Хендлер для вибору користувача зі списку
@router.callback_query(
    AdminCallback.filter(F.action == "select_user"),
    StateFilter(AdminStates.user_management, AdminStates.set_access_level)
)
async def process_select_user(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool,
    callback_data: AdminCallback
) -> None:
    user_id_to_manage = callback_data.user_id
    logger.info(f"Користувач {callback.from_user.id} обрав користувача {user_id_to_manage} для управління.")

    if not user_id_to_manage:
        await callback.answer("Помилка: Не вказано ID користувача.", show_alert=True)
        return

    user_info = await get_user(db_pool, user_id_to_manage)
    if not user_info:
        await callback.answer("Користувача не знайдено.", show_alert=True)
        # Якщо користувача не знайдено, повертаємо до списку користувачів
        current_page = (await state.get_data()).get("users_list_page", 0)
        await _show_users_list_handler(callback, state, db_pool, current_page)
        return

    is_auth = await is_user_authorized(db_pool, user_id_to_manage)
    current_level = user_info.get('access_level', 0)
    
    await state.update_data(selected_user_id=user_id_to_manage, current_user_access_level=current_level)
    await state.set_state(AdminStates.user_management)

    user_info_text = get_user_details_text(user_info, is_auth, ACCESS_LEVEL_BUTTONS)
    keyboard = get_user_actions_keyboard(is_auth, current_level, user_id_to_manage)
    
    await callback.message.edit_text(
        user_info_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


# Хендлер для авторизації/деавторизації користувача
@router.callback_query(UserActionCallback.filter(F.action.in_({"authorize", "unauthorize"})), AdminStates.user_management)
async def process_authorize_unauthorize_user(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: UserActionCallback
) -> None:
    user_id_to_manage = callback_data.target_user_id
    action = callback_data.action
    
    logger.info(f"Користувач {callback.from_user.id} ініціював {action} для користувача {user_id_to_manage}.")

    await state.update_data(pending_action=action, pending_user_id=user_id_to_manage)
    await state.set_state(AdminStates.confirm_action)

    confirm_text = ""
    if action == "authorize":
        confirm_text = f"Ви впевнені, що хочете <b>авторизувати</b> користувача <code>{user_id_to_manage}</code>?"
    else:
        confirm_text = f"Ви впевнені, що хочете <b>деавторизувати</b> користувача <code>{user_id_to_manage}</code>?"
    
    keyboard = get_confirm_action_keyboard(action, user_id_to_manage)

    await callback.message.edit_text(
        confirm_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


# Хендлер для підтвердження авторизації/деавторизації/зміни рівня
@router.callback_query(
    F.data.startswith("user_action:confirm_") | F.data.startswith("access_level:confirm_"),
    AdminStates.confirm_action
)
async def confirm_action(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool,
) -> None:
    state_data = await state.get_data()
    user_id_to_manage = state_data.get("pending_user_id")
    action_type = state_data.get("pending_action")

    if user_id_to_manage is None or action_type is None:
        logger.error(f"Помилка: Неповні дані в FSMContext для підтвердження дії користувача {callback.from_user.id}.")
        await callback.answer("Помилка: Не вдалося виконати дію через відсутність даних. Спробуйте знову.", show_alert=True)
        # Спробуємо повернути до списку, якщо дані втрачено
        current_page = state_data.get("users_list_page", 0)
        await state.set_state(AdminStates.user_management)
        await _show_users_list_handler(callback, state, db_pool, current_page)
        return

    logger.info(f"Користувач {callback.from_user.id} підтвердив {action_type} для користувача {user_id_to_manage}.")

    success_message = ""
    error_message = ""

    try:
        if action_type == "authorize":
            logger.info(f"Спроба зміни статусу авторизації для user_id={user_id_to_manage} на TRUE.")
            await update_user_authorization_status(db_pool, user_id_to_manage, True)
            success_message = f"Користувача <code>{user_id_to_manage}</code> успішно <b>авторизовано</b>."
            error_message = f"Помилка авторизації користувача <code>{user_id_to_manage}</code>."
        elif action_type == "unauthorize":
            logger.info(f"Спроба зміни статусу авторизації для user_id={user_id_to_manage} на FALSE.")
            await update_user_authorization_status(db_pool, user_id_to_manage, False)
            success_message = f"Користувача <code>{user_id_to_manage}</code> успішно <b>деавторизовано</b>."
            error_message = f"Помилка деавторизації користувача <code>{user_id_to_manage}</code>."
        elif action_type == "set_level":
            new_level = state_data.get("pending_level")
            
            if new_level is None:
                logger.error(f"Помилка: 'pending_level' не знайдено в FSMContext для користувача {user_id_to_manage}.")
                await callback.message.edit_text("Помилка: Не вдалося визначити новий рівень доступу.", parse_mode=ParseMode.HTML)
                await _return_to_user_management(callback, state, db_pool, user_id_to_manage)
                return

            logger.info(f"Спроба оновлення рівня доступу для user_id={user_id_to_manage} на рівень={new_level}.")
            await update_user_access_level(db_pool, user_id_to_manage, new_level)
            level_name = next((name for level, name in ACCESS_LEVEL_BUTTONS if level == new_level), str(new_level))
            success_message = f"Рівень доступу користувача <code>{user_id_to_manage}</code> змінено на <b>{level_name} ({new_level})</b>."
            error_message = f"Помилка зміни рівня доступу користувача <code>{user_id_to_manage}</code> на {new_level}."
        else:
            await callback.answer("Невідома дія підтвердження.", show_alert=True)
            return

        await callback.message.edit_text(success_message, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Помилка під час {action_type} користувача {user_id_to_manage}: {e}", exc_info=True)
        await callback.message.edit_text(error_message + f" Причина: {e}", parse_mode=ParseMode.HTML)
    finally:
        await state.update_data(pending_action=None, pending_user_id=None, pending_level=None)
        await _return_to_user_management(callback, state, db_pool, user_id_to_manage)


# Хендлер для скасування дії (повернення до попереднього кроку)
@router.callback_query(AdminCallback.filter(F.action == "cancel_action"), AdminStates.confirm_action)
async def cancel_action(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool
) -> None:
    logger.info(f"Користувач {callback.from_user.id} скасував дію.")
    state_data = await state.get_data()
    user_id_to_manage = state_data.get("pending_user_id")

    await state.update_data(pending_action=None, pending_user_id=None, pending_level=None)

    if user_id_to_manage:
        await _return_to_user_management(callback, state, db_pool, user_id_to_manage)
    else:
        # Якщо немає pending_user_id, повертаємо до загального списку користувачів
        current_page = state_data.get("users_list_page", 0)
        await state.set_state(AdminStates.user_management)
        await _show_users_list_handler(callback, state, db_pool, current_page)


# Хендлер для зміни рівня доступу
@router.callback_query(AdminCallback.filter(F.action == "change_access_level"), AdminStates.user_management)
async def process_change_access_level(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: AdminCallback
) -> None:
    user_id_to_manage = callback_data.user_id
    logger.info(f"Користувач {callback.from_user.id} ініціював зміну рівня доступу для {user_id_to_manage}.")

    await state.set_state(AdminStates.set_access_level)
    await state.update_data(selected_user_id=user_id_to_manage)
    
    keyboard = get_access_level_keyboard(user_id_to_manage)
    
    await callback.message.edit_text(
        f"Оберіть новий рівень доступу для користувача <code>{user_id_to_manage}</code>:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# Хендлер для вибору нового рівня доступу
@router.callback_query(AccessLevelCallback.filter(), AdminStates.set_access_level)
async def set_new_access_level(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool, # Додано db_pool, бо використовується в _return_to_user_management
    callback_data: AccessLevelCallback
) -> None:
    new_level = callback_data.level
    user_id_to_manage = callback_data.target_user_id
    
    logger.info(f"Користувач {callback.from_user.id} обрав рівень доступу {new_level} для користувача {user_id_to_manage}.")

    if not user_id_to_manage:
        await callback.answer("Помилка: ID користувача не знайдено для зміни рівня доступу.", show_alert=True)
        # Важливо мати user_id_to_manage для _return_to_user_management. Якщо він втрачений,
        # краще повернути до загального списку.
        current_page = (await state.get_data()).get("users_list_page", 0)
        await state.set_state(AdminStates.user_management)
        await _show_users_list_handler(callback, state, db_pool, current_page)
        return
    
    await state.update_data(pending_action="set_level", pending_user_id=user_id_to_manage, pending_level=new_level)
    await state.set_state(AdminStates.confirm_action)

    level_name = next((name for level, name in ACCESS_LEVEL_BUTTONS if level == new_level), str(new_level))

    confirm_text = (
        f"Ви впевнені, що хочете змінити рівень доступу для користувача "
        f"<code>{user_id_to_manage}</code> на <b>{level_name} ({new_level})</b>?"
    )
    keyboard = get_confirm_action_keyboard("set_level", user_id_to_manage, new_level)

    await callback.message.edit_text(
        confirm_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()