# handlers/admin_handler.py
import logging
from typing import Any, List
from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from common.keyboards import (
    get_admin_main_keyboard,
    get_users_list_keyboard,
    get_user_actions_keyboard,
    get_confirm_action_keyboard,
    get_access_level_keyboard,
    get_telethon_actions_keyboard,
    get_main_menu_keyboard
)
from common.callbacks import (
    AdminCallback,
    UserActionCallback,
    AccessLevelCallback
)
from common.states import AdminStates
from database import users_db
from common.constants import BUTTONS_PER_PAGE, ACCESS_LEVEL_BUTTONS, MAX_DIALOGS_TO_SHOW
from common.messages import (
    ADMIN_WELCOME_MESSAGE_DEFAULT,
    ADMIN_RETURN_MAIN_PANEL,
    ADMIN_EXIT_MESSAGE,
    ADMIN_USER_MATRIX_PROMPT,
    ADMIN_USER_NOT_FOUND,
    ADMIN_ERROR_NO_USER_ID,
    ADMIN_ERROR_NO_CONFIRM_DATA,
    ADMIN_ERROR_UNKNOWN_STEP,
    ADMIN_ACTION_CANCELED,
    ADMIN_TELETHON_MAIN_PROMPT,
    ADMIN_TELETHON_ALREADY_CONNECTED,
    ADMIN_TELETHON_AUTH_START,
    ADMIN_TELETHON_ENTER_PHONE,
    ADMIN_TELETHON_INVALID_PHONE,
    ADMIN_TELETHON_CODE_SENT,
    ADMIN_TELETHON_ENTER_CODE,
    ADMIN_TELETHON_NO_PHONE_IN_STATE,
    ADMIN_TELETHON_CHECKING_CODE,
    ADMIN_TELETHON_AUTH_SUCCESS,
    ADMIN_TELETHON_CLIENT_NOT_CONNECTED,
    ADMIN_TELETHON_GET_INFO_PROMPT,
    ADMIN_TELETHON_JOIN_CHANNEL_PROMPT,
    ADMIN_TELETHON_JOIN_CHANNEL_SUCCESS,
    ADMIN_TELETHON_CHATS_LOADING,
    ADMIN_TELETHON_NO_CHATS_FOUND,
    ADMIN_TELETHON_PARTIAL_CHATS_INFO,
    ADMIN_TELETHON_CHECK_STATUS_CONNECTED,
    ADMIN_USER_ACCESS_LEVEL_PROMPT,
    ADMIN_USER_ACCESS_LEVEL_CHANGED,
    ADMIN_USER_MANAGEMENT_ACTION_CONFIRM,
    ADMIN_USER_MANAGEMENT_ACTION_SUCCESS,
    ADMIN_ACTION_CANCELED_USER_MANAGEMENT,
    ADMIN_GENERAL_ERROR_RETURN_TO_MAIN,
    ADMIN_ACTION_CANCELED_ALERT,
    ADMIN_ACCESS_LEVEL_CHANGED_ALERT,
    ADMIN_USER_ACTION_SUCCESS_ALERT,
    get_user_details_text
)

logger = logging.getLogger(__name__)
router = Router()


# ----------------------------------------------------------------------
# Допоміжні функції
# ----------------------------------------------------------------------

async def _send_admin_welcome_message(message: types.Message, state: FSMContext) -> None:
    """Відправляє дефолтне привітальне повідомлення адміну."""
    welcome_admin_text = ADMIN_WELCOME_MESSAGE_DEFAULT
    await state.set_state(AdminStates.admin_main)
    await message.answer(
        welcome_admin_text,
        reply_markup=get_admin_main_keyboard(),
        parse_mode=ParseMode.HTML
    )

async def _get_user_info_text(db_pool: Any, user_id: int) -> str:
    """Форматує інформацію про користувача для відображення."""
    user = await users_db.get_user(db_pool, user_id)
    if not user:
        return ADMIN_USER_NOT_FOUND
    return get_user_details_text(user, user.get('is_authorized', False), ACCESS_LEVEL_BUTTONS)

async def _return_to_user_management(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: Any, # Тип змінено на Any
    user_id_to_manage: int,
    status_message: str = None
) -> None:
    """
    Повертає до меню управління конкретним користувачем, оновлюючи інформацію та клавіатуру.
    """
    await state.set_state(AdminStates.user_management)
    await state.update_data(pending_action=None, temp_access_level=None)

    user_info_text = await _get_user_info_text(db_pool, user_id_to_manage)
    user_data = await users_db.get_user(db_pool, user_id_to_manage)
    if not user_data:
        await callback.message.edit_text(
            ADMIN_USER_NOT_FOUND,
            reply_markup=get_admin_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AdminStates.admin_main)
        return

    keyboard = get_user_actions_keyboard(
        is_authorized=user_data['is_authorized'],
        current_access_level=user_data['access_level'],
        user_id_to_manage=user_id_to_manage
    )

    final_text = ""
    if status_message:
        final_text += f"{status_message}\n\n"
    final_text += user_info_text

    await callback.message.edit_text(
        final_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

async def _get_active_telethon_client(telethon_manager: Any, callback: types.CallbackQuery = None) -> Any | None:
    """
    Повертає активний Telethon клієнт. Якщо клієнт не знайдений або не підключений,
    надсилає попередження через callback.answer (якщо надано) та повертає None.
    """
    if telethon_manager and telethon_manager.clients:
        for phone_number, client_obj in telethon_manager.clients.items():
            if client_obj.is_connected():
                return client_obj
    
    if callback:
        await callback.answer(ADMIN_TELETHON_CLIENT_NOT_CONNECTED, show_alert=True)
    return None

# ----------------------------------------------------------------------
# Хендлери для головного адмін-меню
# ----------------------------------------------------------------------

@router.callback_query(
    AdminCallback.filter(F.action == "cancel_admin_action"),
    StateFilter(AdminStates.user_management, AdminStates.telethon_management, AdminStates.set_access_level, AdminStates.confirm_action, AdminStates.waiting_for_telethon_input)
)
async def cancel_admin_action(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Хендлер для скасування поточної адмін-дії та повернення до головного адмін-меню."""
    logger.info(f"Користувач {callback.from_user.id} скасував адмін-дію і повертається до головного адмін-меню.")
    await state.set_state(AdminStates.admin_main)
    await state.update_data(
        pending_action=None,
        selected_user_id=None,
        temp_access_level=None,
        telethon_auth_step=None,
        telethon_phone_number=None,
        telethon_client_session_name=None
    )
    await callback.message.edit_text(
        ADMIN_RETURN_MAIN_PANEL,
        reply_markup=get_admin_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer(ADMIN_ACTION_CANCELED_ALERT)

@router.callback_query(
    AdminCallback.filter(F.action == "close_admin_panel"),
    StateFilter(AdminStates)
)
async def close_admin_panel(
    callback: types.CallbackQuery,
    db_pool: Any, # Тепер ін'єктується
    state: FSMContext
) -> None:
    """Хендлер для закриття адмін-панелі та повернення до головного меню користувача."""
    from handlers.menu_handler import MenuStates

    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} закриває адмін-панель.")
    await state.clear()
    await state.set_state(MenuStates.main_menu)

    access_level = await users_db.get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning(f"Не вдалося видалити інлайн-клавіатуру при закритті адмін-панелі: {e}")
        pass

    await callback.message.answer(
        ADMIN_EXIT_MESSAGE,
        reply_markup=await get_main_menu_keyboard(access_level, page=0),
        parse_mode=ParseMode.HTML
    )
    await callback.answer(ADMIN_EXIT_MESSAGE)
    logger.info(f"Адмін-панель закрито для користувача {user_id}.")


@router.callback_query(
    AdminCallback.filter(F.action == "show_users"),
    StateFilter(AdminStates.admin_main, AdminStates.user_management)
)
async def show_users_list(
    callback: types.CallbackQuery,
    callback_data: AdminCallback,
    db_pool: Any, # Тепер ін'єктується
    state: FSMContext
) -> None:
    """Показує список користувачів з пагінацією."""
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув 'Юзер-матриця'.")
    await state.set_state(AdminStates.user_management)

    users = await users_db.get_all_users(db_pool)
    users.sort(key=lambda u: u.get('registered_at', u.get('id')), reverse=True)

    current_page = callback_data.page if callback_data.page is not None else 0
    users_per_page = BUTTONS_PER_PAGE

    keyboard = get_users_list_keyboard(users, current_page, users_per_page)
    await callback.message.edit_text(
        ADMIN_USER_MATRIX_PROMPT,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@router.callback_query(
    AdminCallback.filter(F.action == "select_user"),
    StateFilter(AdminStates.user_management, AdminStates.set_access_level)
)
async def select_user_from_list(
    callback: types.CallbackQuery,
    callback_data: AdminCallback,
    db_pool: Any, # Тепер ін'єктується
    state: FSMContext
) -> None:
    """Вибирає користувача зі списку для подальшого управління."""
    selected_user_id = callback_data.user_id
    if selected_user_id is None:
        await callback.answer(ADMIN_ERROR_NO_USER_ID, show_alert=True)
        return

    logger.info(f"Адмін {callback.from_user.id} обрав користувача {selected_user_id} для управління.")
    await state.update_data(selected_user_id=selected_user_id)

    await _return_to_user_management(callback, state, db_pool, selected_user_id)
    await callback.answer()

# ----------------------------------------------------------------------
# Хендлери для дій з користувачем (авторизація/деавторизація)
# ----------------------------------------------------------------------

@router.callback_query(
    UserActionCallback.filter(F.action.in_({"authorize", "unauthorize"})),
    StateFilter(AdminStates.user_management)
)
async def request_authorization_confirm(
    callback: types.CallbackQuery,
    callback_data: UserActionCallback,
    state: FSMContext
) -> None:
    """Запитує підтвердження для авторизації/деавторизації користувача."""
    selected_user_id = callback_data.user_id
    action_type = callback_data.action

    logger.info(f"Адмін {callback.from_user.id} запросив підтвердження для {action_type} користувача {selected_user_id}.")

    await state.set_state(AdminStates.confirm_action)
    await state.update_data(
        selected_user_id=selected_user_id,
        pending_action=action_type
    )

    action_text = "авторизувати" if action_type == "authorize" else "деавторизувати"
    question_text = ADMIN_USER_MANAGEMENT_ACTION_CONFIRM.format(action_text=action_text, user_id=selected_user_id)
    keyboard = get_confirm_action_keyboard(action=action_type, user_id=selected_user_id)

    await callback.message.edit_text(
        question_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@router.callback_query(
    UserActionCallback.filter(F.action.in_({"confirm_authorize", "confirm_unauthorize"})),
    StateFilter(AdminStates.confirm_action)
)
async def confirm_authorization_action(
    callback: types.CallbackQuery,
    callback_data: UserActionCallback,
    db_pool: Any, # Тепер ін'єктується
    state: FSMContext
) -> None:
    """Підтверджує та виконує авторизацію/деавторизацію користувача."""
    state_data = await state.get_data()
    selected_user_id = state_data.get("selected_user_id")
    pending_action = state_data.get("pending_action")

    if not selected_user_id or not pending_action:
        await callback.answer(ADMIN_ERROR_NO_CONFIRM_DATA, show_alert=True)
        await callback.message.edit_text(
            ADMIN_GENERAL_ERROR_RETURN_TO_MAIN,
            reply_markup=get_admin_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AdminStates.admin_main)
        return

    is_authorized = (pending_action == "authorize")
    await users_db.update_user_authorization_status(db_pool, selected_user_id, is_authorized)

    status_text = "авторизовано" if is_authorized else "деавторизовано"
    logger.info(f"Користувача {selected_user_id} було {status_text} адміністратором {callback.from_user.id}.")

    await _return_to_user_management(
        callback,
        state,
        db_pool,
        selected_user_id,
        status_message=ADMIN_USER_MANAGEMENT_ACTION_SUCCESS.format(user_id=selected_user_id, status_text=status_text)
    )
    await callback.answer(ADMIN_USER_ACTION_SUCCESS_ALERT.format(user_id=selected_user_id, status_text=status_text))

@router.callback_query(
    AdminCallback.filter(F.action == "cancel_action"),
    StateFilter(AdminStates.confirm_action, AdminStates.set_access_level, AdminStates.waiting_for_telethon_input) # Додано, щоб покрити скасування введення Telethon
)
async def cancel_pending_action(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: Any # Тепер ін'єктується
) -> None:
    """Скасовує очікувану дію та повертає до попереднього стану."""
    state_data = await state.get_data()
    selected_user_id = state_data.get("selected_user_id")
    current_state = await state.get_state()

    logger.info(f"Адмін {callback.from_user.id} скасував очікувану дію для користувача {selected_user_id}.")

    if selected_user_id and current_state in [AdminStates.confirm_action, AdminStates.set_access_level]:
        # Якщо дія скасована під час управління користувачем, повертаємося до його деталей
        await _return_to_user_management(
            callback,
            state,
            db_pool,
            selected_user_id,
            status_message=ADMIN_ACTION_CANCELED_USER_MANAGEMENT.format(user_id=selected_user_id)
        )
    elif current_state == AdminStates.waiting_for_telethon_input:
        # Якщо скасовано введення для Telethon, повертаємось до меню Telethon
        await state.set_state(AdminStates.telethon_management)
        await state.update_data(telethon_auth_step=None, telethon_phone_number=None)
        await callback.message.edit_text(
            f"{ADMIN_ACTION_CANCELED}. {ADMIN_TELETHON_MAIN_PROMPT}",
            reply_markup=get_telethon_actions_keyboard(),
            parse_mode=ParseMode.HTML
        )
    else:
        # В іншому випадку (наприклад, якщо вибраний користувач ID зник або інший невідомий сценарій), повертаємося до головного меню
        await callback.message.edit_text(
            f"{ADMIN_ACTION_CANCELED}. {ADMIN_RETURN_MAIN_PANEL}",
            reply_markup=get_admin_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AdminStates.admin_main)
    await callback.answer(ADMIN_ACTION_CANCELED_ALERT)

# ----------------------------------------------------------------------
# Хендлери для зміни рівня доступу
# ----------------------------------------------------------------------

@router.callback_query(
    AdminCallback.filter(F.action == "change_access_level"),
    StateFilter(AdminStates.user_management)
)
async def request_change_access_level(
    callback: types.CallbackQuery,
    callback_data: AdminCallback,
    state: FSMContext
) -> None:
    """Запитує зміну рівня доступу для користувача."""
    selected_user_id = callback_data.user_id
    if selected_user_id is None:
        await callback.answer(ADMIN_ERROR_NO_USER_ID, show_alert=True)
        return

    logger.info(f"Адмін {callback.from_user.id} запросив зміну рівня доступу для користувача {selected_user_id}.")
    await state.set_state(AdminStates.set_access_level)
    await state.update_data(selected_user_id=selected_user_id)

    keyboard = get_access_level_keyboard(selected_user_id)
    await callback.message.edit_text(
        ADMIN_USER_ACCESS_LEVEL_PROMPT.format(user_id=selected_user_id),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@router.callback_query(
    AccessLevelCallback.filter(),
    StateFilter(AdminStates.set_access_level)
)
async def confirm_set_access_level(
    callback: types.CallbackQuery,
    callback_data: AccessLevelCallback,
    state: FSMContext,
    db_pool: Any # Тепер ін'єктується
) -> None:
    """Підтверджує та встановлює новий рівень доступу для користувача."""
    selected_user_id = callback_data.user_id
    new_access_level = callback_data.level

    if selected_user_id is None or new_access_level is None:
        await callback.answer(ADMIN_ERROR_NO_CONFIRM_DATA, show_alert=True)
        await callback.message.edit_text(
            ADMIN_GENERAL_ERROR_RETURN_TO_MAIN,
            reply_markup=get_admin_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AdminStates.admin_main)
        return

    logger.info(f"Адмін {callback.from_user.id} встановлює рівень доступу {new_access_level} для користувача {selected_user_id}.")

    await users_db.update_user_access_level(db_pool, selected_user_id, new_access_level)

    await _return_to_user_management(
        callback,
        state,
        db_pool,
        selected_user_id,
        status_message=ADMIN_USER_ACCESS_LEVEL_CHANGED.format(user_id=selected_user_id, access_level=new_access_level)
    )
    await callback.answer(ADMIN_ACCESS_LEVEL_CHANGED_ALERT.format(access_level=new_access_level))

# ----------------------------------------------------------------------
# Хендлери для Telethon
# ----------------------------------------------------------------------

@router.callback_query(
    AdminCallback.filter(F.action == "telethon_auth"),
    StateFilter(AdminStates.admin_main, AdminStates.telethon_management)
)
async def process_telethon_auth(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    """Відкриває меню управління Telethon-клієнтами."""
    logger.info(f"Користувач {callback.from_user.id} натиснув 'TeleKey · Авторизація API-зв’язку'.")
    await state.set_state(AdminStates.telethon_management)
    keyboard = get_telethon_actions_keyboard()
    await callback.message.edit_text(
        ADMIN_TELETHON_MAIN_PROMPT,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@router.callback_query(
    AdminCallback.filter(F.action == "telethon_check_status"),
    StateFilter(AdminStates.telethon_management)
)
async def telethon_check_status(
    callback: types.CallbackQuery,
    telethon_manager: Any, # Ін'єктується
    state: FSMContext
) -> None:
    """Перевіряє статус підключення Telethon-клієнта."""
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} перевіряє статус Telethon.")

    active_client = await _get_active_telethon_client(telethon_manager, callback)
    if not active_client:
        return # _get_active_telethon_client вже відправив попередження

    msg = ADMIN_TELETHON_CHECK_STATUS_CONNECTED.format(phone_number=active_client.phone)
    await callback.answer(msg, show_alert=True)

@router.callback_query(
    AdminCallback.filter(F.action == "telethon_start_auth"),
    StateFilter(AdminStates.telethon_management)
)
async def telethon_start_auth(
    callback: types.CallbackQuery,
    telethon_manager: Any, # Ін'єктується
    state: FSMContext
) -> None:
    """Ініціює процес авторизації нового Telethon-клієнта."""
    logger.info(f"Користувач {callback.from_user.id} ініціює авторизацію Telethon.")

    if await _get_active_telethon_client(telethon_manager):
        await callback.answer(ADMIN_TELETHON_ALREADY_CONNECTED, show_alert=True)
        return

    await callback.answer(ADMIN_TELETHON_AUTH_START, show_alert=True)

    await callback.message.edit_text(
        ADMIN_TELETHON_ENTER_PHONE,
        reply_markup=get_telethon_actions_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_telethon_input)
    await state.update_data(telethon_auth_step="phone_number")


@router.message(StateFilter(AdminStates.waiting_for_telethon_input))
async def handle_telethon_input(
    message: types.Message,
    state: FSMContext,
    telethon_manager: Any # Ін'єктується
):
    """Обробляє вхідні дані для авторизації Telethon (номер телефону, код)."""
    user_id = message.from_user.id
    state_data = await state.get_data()
    auth_step = state_data.get("telethon_auth_step")
    user_input = message.text

    if auth_step == "phone_number":
        phone_number = user_input
        if not phone_number or not phone_number.startswith('+') or not phone_number[1:].isdigit():
            await message.answer(ADMIN_TELETHON_INVALID_PHONE)
            return

        logger.info(f"Отримано номер телефону для Telethon від {user_id}: {phone_number}")
        # Глобальний обробник винятків перехопить помилки send_code
        await telethon_manager.send_code(phone_number)
        await message.answer(ADMIN_TELETHON_CODE_SENT.format(phone_number=phone_number))
        await state.update_data(telethon_auth_step="auth_code", telethon_phone_number=phone_number)

    elif auth_step == "auth_code":
        auth_code = user_input
        if not auth_code or not auth_code.isdigit():
            await message.answer(ADMIN_TELETHON_ENTER_CODE)
            return

        logger.info(f"Отримано код авторизації для Telethon від {user_id}: {auth_code}")
        phone_number = state_data.get("telethon_phone_number")

        if not phone_number:
            await message.answer(ADMIN_TELETHON_NO_PHONE_IN_STATE)
            await state.set_state(AdminStates.telethon_management)
            return

        await message.answer(ADMIN_TELETHON_CHECKING_CODE)
        # Глобальний обробник винятків перехопить помилки sign_in
        await telethon_manager.sign_in(phone_number, auth_code)
        auth_status_msg = ADMIN_TELETHON_AUTH_SUCCESS
        logger.info(f"Клієнт {phone_number} успішно авторизований через Telethon.")

        await state.set_state(AdminStates.telethon_management)
        await state.update_data(telethon_auth_step=None, telethon_phone_number=None)
        await message.answer(
            auth_status_msg,
            reply_markup=get_telethon_actions_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif auth_step == "join_channel":
        channel_link_or_username = user_input.strip()
        logger.info(f"Користувач {user_id} надіслав посилання/username для приєднання Telethon: {channel_link_or_username}")

        active_client = await _get_active_telethon_client(telethon_manager)
        if not active_client:
            await message.answer(ADMIN_TELETHON_CLIENT_NOT_CONNECTED, reply_markup=get_telethon_actions_keyboard())
            await state.set_state(AdminStates.telethon_management)
            return

        # Глобальний обробник винятків перехопить помилки join_chat
        await active_client.join_chat(channel_link_or_username)
        join_status_msg = ADMIN_TELETHON_JOIN_CHANNEL_SUCCESS.format(channel_link_or_username=channel_link_or_username)
        logger.info(f"Telethon клієнт успішно приєднався до {channel_link_or_username}.")

        await message.answer(
            join_status_msg,
            reply_markup=get_telethon_actions_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AdminStates.telethon_management)
        await state.update_data(telethon_auth_step=None)
    else:
        await message.answer(ADMIN_ERROR_UNKNOWN_STEP)
        await state.set_state(AdminStates.telethon_management)

@router.callback_query(
    AdminCallback.filter(F.action == "telethon_get_user_info"),
    StateFilter(AdminStates.telethon_management)
)
async def telethon_get_user_info(
    callback: types.CallbackQuery,
    telethon_manager: Any, # Ін'єктується
    state: FSMContext
) -> None:
    """Отримує та відображає інформацію про поточного Telethon-користувача."""
    logger.info(f"Користувач {callback.from_user.id} запросив інформацію про Telethon користувача.")

    active_client = await _get_active_telethon_client(telethon_manager, callback)
    if not active_client:
        return

    await callback.answer(ADMIN_TELETHON_GET_INFO_PROMPT, show_alert=True)

    # Глобальний обробник винятків перехопить помилки get_me
    me = await active_client.get_me()
    user_info_text = (
        f"<b>Інформація про поточного Telethon користувача:</b>\n"
        f"  <b>ID:</b> <code>{me.id}</code>\n"
        f"  <b>Ім'я:</b> {me.first_name if me.first_name else 'Не вказано'}\n"
        f"  <b>Прізвище:</b> {me.last_name if me.last_name else 'Не вказано'}\n"
        f"  <b>Username:</b> @{me.username if me.username else 'Не вказано'}\n"
        f"  <b>Телефон:</b> {me.phone if me.phone else 'Не вказано'}\n"
    )

    await callback.message.edit_text(
        user_info_text,
        reply_markup=get_telethon_actions_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AdminStates.telethon_management)
    await callback.answer()

@router.callback_query(
    AdminCallback.filter(F.action == "telethon_join_channel"),
    StateFilter(AdminStates.telethon_management)
)
async def telethon_join_channel(
    callback: types.CallbackQuery,
    telethon_manager: Any, # Ін'єктується
    state: FSMContext
) -> None:
    """Запитує посилання/username для приєднання Telethon-клієнта до каналу."""
    logger.info(f"Користувач {callback.from_user.id} запросив приєднання Telethon до каналу.")

    active_client = await _get_active_telethon_client(telethon_manager, callback)
    if not active_client:
        return

    await callback.answer(ADMIN_TELETHON_GET_INFO_PROMPT, show_alert=True)
    await callback.message.edit_text(
        ADMIN_TELETHON_JOIN_CHANNEL_PROMPT,
        reply_markup=get_telethon_actions_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AdminStates.waiting_for_telethon_input)
    await state.update_data(telethon_auth_step="join_channel")


@router.callback_query(
    AdminCallback.filter(F.action == "telethon_chats"),
    StateFilter(AdminStates.admin_main, AdminStates.telethon_management)
)
async def show_telethon_chats(
    callback: types.CallbackQuery,
    telethon_manager: Any, # Ін'єктується
    state: FSMContext
) -> None:
    """Показує список діалогів та каналів Telethon-клієнта."""
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув 'Чат-матриця'.")

    await state.set_state(AdminStates.telethon_management)
    await callback.answer(ADMIN_TELETHON_CHATS_LOADING, show_alert=True)

    active_client = await _get_active_telethon_client(telethon_manager, callback)
    if not active_client:
        return

    dialogs_info = "<b>💬 Активні чати та канали:</b>\n\n"
    # Глобальний обробник винятків перехопить помилки get_dialogs
    dialogs: List[Any] = await active_client.get_dialogs()
    logger.debug(f"Successfully received {len(dialogs)} dialogs.")

    if not dialogs:
        dialogs_info += ADMIN_TELETHON_NO_CHATS_FOUND
    else:
        for i, d in enumerate(dialogs[:MAX_DIALOGS_TO_SHOW]):
            entity_type = ""
            if d.is_user:
                entity_type = "👤 Користувач"
            elif d.is_channel:
                entity_type = "📢 Канал"
            elif d.is_group:
                entity_type = "👥 Група"
            
            title = d.title if d.title else "Без назви"
            dialogs_info += f"• {entity_type}: <b>{title}</b> (ID: <code>{d.id}</code>)\n"
            
        if len(dialogs) > MAX_DIALOGS_TO_SHOW:
            dialogs_info += ADMIN_TELETHON_PARTIAL_CHATS_INFO.format(count=MAX_DIALOGS_TO_SHOW, total=len(dialogs))

    await callback.message.edit_text(
        dialogs_info,
        reply_markup=get_telethon_actions_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()