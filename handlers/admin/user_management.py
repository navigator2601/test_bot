# handlers/admin/user_management.py
import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter

import asyncpg

from database.users_db import get_user, update_user_access_level, get_all_users, is_user_authorized, update_user_authorization_status
from keyboards.admin_keyboard import get_users_list_keyboard, get_user_actions_keyboard, get_confirm_action_keyboard, get_access_level_keyboard
from common.constants import USERS_PER_PAGE, ACCESS_LEVEL_BUTTONS
from common.messages import get_access_level_description

# Імпортуємо стани та фільтр адміна
from common.states import AdminStates
from filters.admin_filter import AdminAccessFilter
from keyboards.callback_factories import AdminCallback, UserActionCallback, AccessLevelCallback

logger = logging.getLogger(__name__)

router = Router()

# Застосовуємо фільтр адмін-доступу до всього роутера
router.callback_query.filter(AdminAccessFilter())
router.message.filter(AdminAccessFilter()) # Хоча в цьому роутері немає message хендлерів, це безпечно


# Хендлер для вибору користувача зі списку
@router.callback_query(AdminCallback.filter(F.action == "select_user"), AdminStates.user_management)
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
        return

    is_auth = await is_user_authorized(db_pool, user_id_to_manage)
    current_level = user_info.get('access_level', 0)
    
    # Оновлюємо FSM-дані, щоб зберігати ID користувача, яким керуємо
    await state.update_data(selected_user_id=user_id_to_manage, current_user_access_level=current_level)

    keyboard = get_user_actions_keyboard(is_auth, current_level, user_id_to_manage)
    
    access_level_name, _ = get_access_level_description(current_level, ACCESS_LEVEL_BUTTONS)
    user_info_text = (
        f"<b>🛠️ Управління користувачем:</b>\n\n"
        f"<b>ID:</b> <code>{user_info.get('id')}</code>\n"
        f"<b>Ім'я:</b> {user_info.get('first_name', 'N/A')} {user_info.get('last_name', '')}\n"
        f"<b>Username:</b> @{user_info.get('username', 'N/A')}\n"
        f"<b>Рівень доступу:</b> {access_level_name} ({current_level})\n"
        f"<b>Статус:</b> {'Авторизований ✅' if is_auth else 'Неавторизований ❌'}"
    )

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
    user_id_to_manage = callback_data.user_id
    action = callback_data.action # 'authorize' або 'unauthorize'
    
    logger.info(f"Користувач {callback.from_user.id} ініціював {action} для користувача {user_id_to_manage}.")

    # Зберігаємо дію для підтвердження
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


# Хендлер для підтвердження авторизації/деавторизації
@router.callback_query(UserActionCallback.filter(F.action.startswith("confirm_")), AdminStates.confirm_action)
async def confirm_authorize_unauthorize_user(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool,
    callback_data: UserActionCallback # Цей callback_data може бути UserActionCallback або AccessLevelCallback
) -> None:
    user_id_to_manage = callback_data.user_id
    action_type = callback_data.action.replace("confirm_", "") # 'authorize', 'unauthorize' або 'set_level'

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
            # ВИПРАВЛЕНО: Отримуємо new_level з FSMContext
            state_data = await state.get_data()
            new_level = state_data.get("pending_level")
            
            if new_level is None:
                logger.error(f"Помилка: 'pending_level' не знайдено в FSMContext для користувача {user_id_to_manage}.")
                await callback.message.edit_text("Помилка: Не вдалося визначити новий рівень доступу.", parse_mode=ParseMode.HTML)
                await state.set_state(AdminStates.user_management)
                await callback.answer()
                return

            logger.info(f"Спроба оновлення рівня доступу для user_id={user_id_to_manage} на рівень={new_level}.")
            await update_user_access_level(db_pool, user_id_to_manage, new_level)
            success_message = f"Рівень доступу користувача <code>{user_id_to_manage}</code> змінено на <b>{new_level}</b>."
            error_message = f"Помилка зміни рівня доступу користувача <code>{user_id_to_manage}</code> на {new_level}."
        else:
            await callback.answer("Невідома дія підтвердження.", show_alert=True)
            return

        await state.set_state(AdminStates.user_management)
        await callback.message.edit_text(success_message, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Помилка під час {action_type} користувача {user_id_to_manage}: {e}", exc_info=True)
        await callback.message.edit_text(error_message + f" Причина: {e}", parse_mode=ParseMode.HTML)
    
    # Повертаємось до управління користувачем або списку користувачів
    await state.set_state(AdminStates.user_management)
    # Знову відображаємо інформацію про користувача або список
    user_info = await get_user(db_pool, user_id_to_manage) 
    if user_info:
        is_auth = await is_user_authorized(db_pool, user_id_to_manage)
        current_level = user_info.get('access_level', 0)
        keyboard = get_user_actions_keyboard(is_auth, current_level, user_id_to_manage)
        
        access_level_name, _ = get_access_level_description(current_level, ACCESS_LEVEL_BUTTONS)
        user_info_text = (
            f"<b>🛠️ Управління користувачем:</b>\n\n"
            f"<b>ID:</b> <code>{user_info.get('id')}</code>\n"
            f"<b>Ім'я:</b> {user_info.get('first_name', 'N/A')} {user_info.get('last_name', '')}\n"
            f"<b>Username:</b> @{user_info.get('username', 'N/A')}\n"
            f"<b>Рівень доступу:</b> {access_level_name} ({current_level})\n"
            f"<b>Статус:</b> {'Авторизований ✅' if is_auth else 'Неавторизований ❌'}"
        )
        await callback.message.edit_text(user_info_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        # Якщо користувач не знайдений після дії, повертаємось до списку
        users = await get_all_users(db_pool)
        current_page = (await state.get_data()).get("users_list_page", 0)
        keyboard = get_users_list_keyboard(users, current_page, USERS_PER_PAGE)
        await callback.message.edit_text(
            f"Користувача <code>{user_id_to_manage}</code> оновлено. Оберіть наступного користувача:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    await callback.answer()


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

    if user_id_to_manage:
        user_info = await get_user(db_pool, user_id_to_manage)
        if user_info:
            is_auth = await is_user_authorized(db_pool, user_id_to_manage)
            current_level = user_info.get('access_level', 0)
            keyboard = get_user_actions_keyboard(is_auth, current_level, user_id_to_manage)
            
            access_level_name, _ = get_access_level_description(current_level, ACCESS_LEVEL_BUTTONS)
            user_info_text = (
                f"<b>🛠️ Управління користувачем:</b>\n\n"
                f"<b>ID:</b> <code>{user_info.get('id')}</code>\n"
                f"<b>Ім'я:</b> {user_info.get('first_name', 'N/A')} {user_info.get('last_name', '')}\n"
                f"<b>Username:</b> @{user_info.get('username', 'N/A')}\n"
                f"<b>Рівень доступу:</b> {access_level_name} ({current_level})\n"
                f"<b>Статус:</b> {'Авторизований ✅' if is_auth else 'Неавторизований ❌'}"
            )
            await callback.message.edit_text(user_info_text, reply_markup=keyboard, parse_mode=ParseMode.HTML) 
        else:
            await callback.message.edit_text("Дію скасовано. Користувача не знайдено. Повернення до списку користувачів.",
                                             reply_markup=get_users_list_keyboard(await get_all_users(db_pool), (await state.get_data()).get("users_list_page", 0), USERS_PER_PAGE),
                                             parse_mode=ParseMode.HTML)
    else:
        await callback.message.edit_text("Дію скасовано. Повернення до списку користувачів.",
                                         reply_markup=get_users_list_keyboard(await get_all_users(db_pool), (await state.get_data()).get("users_list_page", 0), USERS_PER_PAGE),
                                         parse_mode=ParseMode.HTML)
    
    await state.set_state(AdminStates.user_management)
    await state.update_data(pending_action=None, pending_user_id=None, pending_level=None) # Очищаємо всі дані про очікувану дію
    await callback.answer()

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
    await state.update_data(selected_user_id=user_id_to_manage) # Зберігаємо user_id_to_manage в FSM
    
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
    callback_data: AccessLevelCallback
) -> None:
    new_level = callback_data.level
    user_id_to_manage = callback_data.user_id # Отримуємо user_id з callback_data
    
    logger.info(f"Користувач {callback.from_user.id} обрав рівень доступу {new_level} для користувача {user_id_to_manage}.")

    if not user_id_to_manage:
        await callback.answer("Помилка: ID користувача не знайдено для зміни рівня доступу.", show_alert=True)
        await state.set_state(AdminStates.user_management) # Повертаємось до списку користувачів
        return
    
    # Переходимо до кроку підтвердження
    await state.update_data(pending_action="set_level", pending_user_id=user_id_to_manage, pending_level=new_level) # <--- ТУТ ЗБЕРІГАЄМО pending_level
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