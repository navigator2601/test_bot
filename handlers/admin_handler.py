# handlers/admin_handler.py

import logging
from aiogram import Router, types, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
import asyncpg
from typing import Any, Optional, List # Додаємо List для типізації
from telethon.tl.types import Dialog # Імпортуємо Dialog для типізації

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
from keyboards.callback_factories import AdminCallback, UserActionCallback, AccessLevelCallback
# from handlers.menu_handler import MenuStates # Цей імпорт тут більше не потріжен через циклічний імпорт

logger = logging.getLogger(__name__)

router = Router()

class AdminStates(StatesGroup):
    admin_main = State()
    user_management = State()
    confirm_action = State()
    set_access_level = State()
    telethon_management = State()
    waiting_for_telethon_input = State()

# ----------------------------------------------------------------------
# Допоміжні функції
# ----------------------------------------------------------------------

async def _send_admin_welcome_message(message: types.Message, state: FSMContext) -> None:
    """Відправляє випадкове привітальне повідомлення адміну."""
    welcome_admin_text = get_random_admin_welcome_message()
    await state.set_state(AdminStates.admin_main)
    await message.answer(
        welcome_admin_text,
        reply_markup=get_admin_main_keyboard(),
        parse_mode=ParseMode.HTML
    )

async def _get_user_info_text(db_pool: asyncpg.Pool, user_id: int) -> str:
    """Форматує інформацію про користувача для відображення."""
    user = await users_db.get_user(db_pool, user_id)
    if not user:
        return "Користувача не знайдено."

    access_level_name, access_level_desc = get_access_level_description(user['access_level'])
    auth_status = "Авторизований ✅" if user['is_authorized'] else "Не авторизований ❌"
    registered_at_local = user['registered_at'].strftime("%Y-%m-%d %H:%M:%S") if user['registered_at'] else "Невідомо"
    last_activity_local = user['last_activity'].strftime("%Y-%m-%d %H:%M:%S") if user['last_activity'] else "Невідомо"

    user_info_text = (
        f"<b>⚙️ Інформація про користувача:</b>\n\n"
        f"  <b>ID:</b> <code>{user['id']}</code>\n"
        f"  <b>Username:</b> @{user['username'] if user['username'] else 'Не вказано'}\n"
        f"  <b>Ім'я:</b> {user['first_name'] if user['first_name'] else 'Не вказано'}\n"
        f"  <b>Прізвище:</b> {user['last_name'] if user['last_name'] else 'Не вказано'}\n"
        f"  <b>Рівень доступу:</b> {user['access_level']} (<i>{access_level_name}</i>)\n"
        f"  <b>Статус авторизації:</b> {auth_status}\n"
        f"  <b>Зареєстрований:</b> {registered_at_local}\n"
        f"  <b>Остання активність:</b> {last_activity_local}\n\n"
        f"<i>{access_level_desc}</i>"
    )
    return user_info_text

# ----------------------------------------------------------------------
# Хендлери для головного адмін-меню
# ----------------------------------------------------------------------

# Хендлер для повернення до головного адмін-меню з будь-якого підменю (загальна кнопка "Назад")
@router.callback_query(
    AdminCallback.filter(F.action == "cancel_admin_action"),
    StateFilter(AdminStates.user_management, AdminStates.telethon_management, AdminStates.set_access_level, AdminStates.confirm_action, AdminStates.waiting_for_telethon_input)
)
async def cancel_admin_action(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    logger.info(f"Користувач {callback.from_user.id} скасував адмін-дію і повертається до головного адмін-меню.")
    await state.set_state(AdminStates.admin_main)
    await state.update_data(pending_action=None, selected_user_id=None, temp_access_level=None, telethon_auth_step=None, telethon_phone_number=None) # Очищаємо тимчасові дані
    await callback.message.edit_text(
        "Ви повернулись до головної адмін-панелі.",
        reply_markup=get_admin_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# Хендлер для закриття адмін-панелі
@router.callback_query(
    AdminCallback.filter(F.action == "close_admin_panel"),
    StateFilter(AdminStates)
)
async def close_admin_panel(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    # Важливо: локальний імпорт MenuStates, щоб уникнути циклічного імпорту
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
        "Ви вийшли з адмін-панелі. Повернення до головного меню.",
        reply_markup=await get_main_menu_keyboard(access_level, 0),
        parse_mode=ParseMode.HTML
    )
    await callback.answer("Адмін-панель закрито.")
    logger.info(f"Адмін-панель закрито для користувача {user_id}.")

# Хендлер для кнопки "👥 Юзер-матриця · Редактор доступу"
@router.callback_query(
    AdminCallback.filter(F.action == "show_users"),
    StateFilter(AdminStates.admin_main, AdminStates.user_management)
)
async def show_users_list(
    callback: types.CallbackQuery,
    callback_data: AdminCallback,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув 'Юзер-матриця'.")
    await state.set_state(AdminStates.user_management)

    users = await users_db.get_all_users(db_pool)
    users.sort(key=lambda u: u.get('registered_at', u.get('id')), reverse=True)

    current_page = callback_data.page if callback_data.page is not None else 0
    users_per_page = BUTTONS_PER_PAGE

    keyboard = get_users_list_keyboard(users, current_page, users_per_page)
    await callback.message.edit_text(
        "<b>👥 Юзер-матриця:</b>\nОберіть користувача для управління або перегляньте сторінки.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# Хендлер для вибору конкретного користувача зі списку
@router.callback_query(
    AdminCallback.filter(F.action == "select_user"),
    StateFilter(AdminStates.user_management, AdminStates.set_access_level)
)
async def select_user_from_list(
    callback: types.CallbackQuery,
    callback_data: AdminCallback,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    selected_user_id = callback_data.user_id
    if selected_user_id is None:
        await callback.answer("Помилка: не знайдено ID користувача.", show_alert=True)
        return

    logger.info(f"Адмін {callback.from_user.id} обрав користувача {selected_user_id} для управління.")
    await state.set_state(AdminStates.user_management)

    await state.update_data(selected_user_id=selected_user_id)

    user_info_text = await _get_user_info_text(db_pool, selected_user_id)
    user_data = await users_db.get_user(db_pool, selected_user_id)
    if not user_data:
        await callback.answer("Помилка: Користувача не знайдено в базі даних.", show_alert=True)
        return

    keyboard = get_user_actions_keyboard(
        is_authorized=user_data['is_authorized'],
        current_access_level=user_data['access_level'],
        user_id_to_manage=selected_user_id
    )
    await callback.message.edit_text(
        user_info_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
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
    selected_user_id = callback_data.user_id
    action_type = callback_data.action

    logger.info(f"Адмін {callback.from_user.id} запросив підтвердження для {action_type} користувача {selected_user_id}.")

    await state.set_state(AdminStates.confirm_action)
    await state.update_data(
        selected_user_id=selected_user_id,
        pending_action=action_type
    )

    action_text = "авторизувати" if action_type == "authorize" else "деавторизувати"
    question_text = f"Ви впевнені, що хочете <b>{action_text}</b> користувача <code>{selected_user_id}</code>?"
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
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    state_data = await state.get_data()
    selected_user_id = state_data.get("selected_user_id")
    pending_action = state_data.get("pending_action")

    if not selected_user_id or not pending_action:
        await callback.answer("Помилка: не знайдено даних для підтвердження.", show_alert=True)
        await state.set_state(AdminStates.admin_main)
        await callback.message.edit_text(
            "Сталася помилка. Повернення до головної адмін-панелі.",
            reply_markup=get_admin_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    is_authorized = (pending_action == "authorize")
    await users_db.update_user_authorization_status(db_pool, selected_user_id, is_authorized)

    status_text = "авторизовано" if is_authorized else "деавторизовано"
    logger.info(f"Користувача {selected_user_id} було {status_text} адміністратором {callback.from_user.id}.")

    await state.set_state(AdminStates.user_management)
    await state.update_data(pending_action=None)

    user_info_text = await _get_user_info_text(db_pool, selected_user_id)
    user_data = await users_db.get_user(db_pool, selected_user_id)
    keyboard = get_user_actions_keyboard(
        is_authorized=user_data['is_authorized'],
        current_access_level=user_data['access_level'],
        user_id_to_manage=selected_user_id
    )

    await callback.message.edit_text(
        f"Користувача <code>{selected_user_id}</code> успішно <b>{status_text}</b>.\n\n{user_info_text}",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer(f"Користувача {selected_user_id} успішно {status_text}.")

@router.callback_query(
    AdminCallback.filter(F.action == "cancel_action"),
    StateFilter(AdminStates.confirm_action)
)
async def cancel_pending_action(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool
) -> None:
    state_data = await state.get_data()
    selected_user_id = state_data.get("selected_user_id")

    logger.info(f"Адмін {callback.from_user.id} скасував очікувану дію для користувача {selected_user_id}.")
    await state.set_state(AdminStates.user_management)
    await state.update_data(pending_action=None)

    if selected_user_id:
        user_info_text = await _get_user_info_text(db_pool, selected_user_id)
        user_data = await users_db.get_user(db_pool, selected_user_id)
        keyboard = get_user_actions_keyboard(
            is_authorized=user_data['is_authorized'],
            current_access_level=user_data['access_level'],
            user_id_to_manage=selected_user_id
        )
        await callback.message.edit_text(
            f"Дію скасовано. Повернення до управління користувачем <code>{selected_user_id}</code>.\n\n{user_info_text}",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        await callback.message.edit_text(
            "Дію скасовано. Повернення до головної адмін-панелі.",
            reply_markup=get_admin_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AdminStates.admin_main)
    await callback.answer("Дію скасовано.")

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
    selected_user_id = callback_data.user_id
    if selected_user_id is None:
        await callback.answer("Помилка: не знайдено ID користувача.", show_alert=True)
        return

    logger.info(f"Адмін {callback.from_user.id} запросив зміну рівня доступу для користувача {selected_user_id}.")
    await state.set_state(AdminStates.set_access_level)
    await state.update_data(selected_user_id=selected_user_id)

    keyboard = get_access_level_keyboard(selected_user_id)
    await callback.message.edit_text(
        f"Оберіть новий рівень доступу для користувача <code>{selected_user_id}</code>:",
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
    db_pool: asyncpg.Pool
) -> None:
    selected_user_id = callback_data.user_id
    new_access_level = callback_data.level

    if selected_user_id is None or new_access_level is None:
        await callback.answer("Помилка: не знайдено даних для зміни рівня доступу.", show_alert=True)
        return

    logger.info(f"Адмін {callback.from_user.id} встановлює рівень доступу {new_access_level} для користувача {selected_user_id}.")

    await users_db.update_user_access_level(db_pool, selected_user_id, new_access_level)

    await state.set_state(AdminStates.user_management)
    await state.update_data(temp_access_level=None)

    user_info_text = await _get_user_info_text(db_pool, selected_user_id)
    user_data = await users_db.get_user(db_pool, selected_user_id)
    keyboard = get_user_actions_keyboard(
        is_authorized=user_data['is_authorized'],
        current_access_level=user_data['access_level'],
        user_id_to_manage=selected_user_id
    )

    await callback.message.edit_text(
        f"Рівень доступу для користувача <code>{selected_user_id}</code> успішно встановлено на <b>{new_access_level}</b>.\n\n{user_info_text}",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer(f"Рівень доступу змінено на {new_access_level}.")

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
    logger.info(f"Користувач {callback.from_user.id} натиснув 'TeleKey · Авторизація API-зв’язку'.")
    await state.set_state(AdminStates.telethon_management)
    keyboard = get_telethon_actions_keyboard()
    await callback.message.edit_text(
        "<b>🔐 TeleKey · Авторизація API-зв’язку:</b>\n\nОберіть дію для управління Telethon API:",
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
    telethon_manager: Any,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} перевіряє статус Telethon.")
    logger.debug(f"Telethon Manager received in telethon_check_status: {telethon_manager}")
    
    # ПРИПУЩЕННЯ: telethon_manager.clients - це словник {phone_number: telethon_client_object}
    # Для перевірки статусу, нам потрібно знати, який клієнт перевіряти.
    # Наразі, візьмемо перший доступний клієнт або за номером телефону, якщо він відомий.
    
    # Припустимо, що у вас є єдиний активний клієнт, або ви хочете перевірити перший, що знайдеться
    first_client_phone = next(iter(telethon_manager.clients), None)
    
    if first_client_phone and telethon_manager.clients[first_client_phone].is_connected():
        msg = f"✅ Telethon клієнт ({first_client_phone}) підключено."
    else:
        msg = "❌ Telethon клієнт не підключено або не знайдено активних клієнтів."

    await callback.answer(msg, show_alert=True)
    await state.set_state(AdminStates.telethon_management)

@router.callback_query(
    AdminCallback.filter(F.action == "telethon_start_auth"),
    StateFilter(AdminStates.telethon_management)
)
async def telethon_start_auth(
    callback: types.CallbackQuery,
    telethon_manager: Any,
    state: FSMContext
) -> None:
    logger.info(f"Користувач {callback.from_user.id} ініціює авторизацію Telethon.")

    # Перевіряємо, чи клієнт вже підключений
    # Потрібно пройтися по всіх клієнтах, або перевірити конкретний, якщо його ідентифіковано
    is_any_client_connected = False
    for phone_number, client_obj in telethon_manager.clients.items():
        if client_obj.is_connected():
            is_any_client_connected = True
            break

    if is_any_client_connected:
        await callback.answer("Принаймні один клієнт Telethon вже підключено. Якщо потрібно переавторизувати, спочатку відключіть.", show_alert=True)
        return

    await callback.answer("Початок авторизації Telethon...", show_alert=True)

    await callback.message.edit_text(
        "Будь ласка, введіть номер телефону для авторизації Telethon (у форматі +380XXXXXXXXX):",
        reply_markup=get_telethon_actions_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_telethon_input)
    await state.update_data(telethon_auth_step="phone_number")


@router.message(StateFilter(AdminStates.waiting_for_telethon_input))
async def handle_telethon_input(message: types.Message, state: FSMContext, telethon_manager: Any):
    user_id = message.from_user.id
    state_data = await state.get_data()
    auth_step = state_data.get("telethon_auth_step")
    user_input = message.text

    if auth_step == "phone_number":
        phone_number = user_input
        if not phone_number or not phone_number.startswith('+') or not phone_number[1:].isdigit():
            await message.answer("Будь ласка, введіть коректний номер телефону у форматі +380XXXXXXXXX.")
            return

        logger.info(f"Отримано номер телефону для Telethon від {user_id}: {phone_number}")
        try:
            # Припускаємо, що telethon_manager має метод send_code, який приймає номер телефону
            # І що він повертає об'єкт TelethonClient для подальшої роботи
            # Або що send_code вже інтегрує його в telethon_manager.clients
            await telethon_manager.send_code(phone_number) # Цей метод має додати клієнта до telethon_manager.clients
            await message.answer(f"Відправлено код підтвердження на номер {phone_number}. Будь ласка, введіть його:")
            await state.update_data(telethon_auth_step="auth_code", telethon_phone_number=phone_number)
        except Exception as e:
            logger.error(f"Помилка при відправці коду Telethon для {phone_number}: {e}")
            await message.answer(
                f"Не вдалося відправити код: {e}. Спробуйте ще раз або перевірте номер.",
                reply_markup=get_telethon_actions_keyboard()
            )
            await state.set_state(AdminStates.telethon_management)


    elif auth_step == "auth_code":
        auth_code = user_input
        if not auth_code or not auth_code.isdigit():
            await message.answer("Будь ласка, введіть коректний цифровий код підтвердження.")
            return

        logger.info(f"Отримано код авторизації для Telethon від {user_id}: {auth_code}")
        phone_number = state_data.get("telethon_phone_number")

        if not phone_number:
            await message.answer("Помилка: номер телефону не знайдено. Спробуйте почати авторизацію знову.")
            await state.set_state(AdminStates.telethon_management)
            return

        try:
            # Припускаємо, що telethon_manager має метод sign_in, який приймає номер телефону та код
            await telethon_manager.sign_in(phone_number, auth_code)
            auth_status_msg = "Авторизація Telethon успішно завершена."
            logger.info(f"Клієнт {phone_number} успішно авторизований через Telethon.")
        except Exception as e:
            auth_status_msg = f"Помилка авторизації Telethon: {e}. Спробуйте ще раз."
            logger.error(f"Помилка авторизації Telethon для {phone_number}: {e}")

        await message.answer("Перевірка коду...")
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

        active_client = None
        if telethon_manager and telethon_manager.clients:
            first_phone = next(iter(telethon_manager.clients), None)
            if first_phone:
                active_client = telethon_manager.clients[first_phone]
        
        if not active_client or not active_client.is_connected():
            await message.answer("Клієнт Telethon не підключено. Будь ласка, авторизуйтесь спочатку.", reply_markup=get_telethon_actions_keyboard())
            await state.set_state(AdminStates.telethon_management)
            return

        try:
            # Припускаємо, що telethon_manager або active_client має метод join_channel
            # Telethon клієнт має метод .join_chat()
            await active_client.join_chat(channel_link_or_username)
            join_status_msg = f"✅ Успішно приєднано до каналу/чату: <code>{channel_link_or_username}</code>"
            logger.info(f"Telethon клієнт успішно приєднався до {channel_link_or_username}.")
        except Exception as e:
            join_status_msg = f"❌ Не вдалося приєднатися до каналу/чату <code>{channel_link_or_username}</code>: {e}"
            logger.error(f"Помилка при приєднанні Telethon до {channel_link_or_username}: {e}", exc_info=True)
        
        await message.answer(
            join_status_msg,
            reply_markup=get_telethon_actions_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await state.set_state(AdminStates.telethon_management)
        await state.update_data(telethon_auth_step=None)
    else:
        await message.answer("Невідомий крок авторизації. Будь ласка, спробуйте знову.")
        await state.set_state(AdminStates.telethon_management)

@router.callback_query(
    AdminCallback.filter(F.action == "telethon_get_user_info"),
    StateFilter(AdminStates.telethon_management)
)
async def telethon_get_user_info(
    callback: types.CallbackQuery,
    telethon_manager: Any,
    state: FSMContext
) -> None:
    logger.info(f"Користувач {callback.from_user.id} запросив інформацію про Telethon користувача.")

    # Отримуємо активний клієнт. Припускаємо, що зараз ми працюємо з одним клієнтом,
    # і що його можна отримати за ключем з `clients`
    # Можливо, вам знадобиться механізм вибору клієнта, якщо їх буде багато
    active_client = None
    if telethon_manager and telethon_manager.clients:
        # Візьмемо перший клієнт, або той, що був останній авторизований/використовуваний
        # У цьому випадку візьмемо перший ключ, якщо є
        first_phone = next(iter(telethon_manager.clients), None)
        if first_phone:
            active_client = telethon_manager.clients[first_phone]

    if not active_client or not active_client.is_connected():
        await callback.answer("Клієнт Telethon не підключено. Будь ласка, авторизуйтесь спочатку.", show_alert=True)
        return

    await callback.answer("Отримання інформації про користувача Telethon...", show_alert=True)

    try:
        me = await active_client.get_me() # Використовуємо active_client
        user_info_text = (
            f"<b>Інформація про поточного Telethon користувача:</b>\n"
            f"  <b>ID:</b> <code>{me.id}</code>\n"
            f"  <b>Ім'я:</b> {me.first_name if me.first_name else 'Не вказано'}\n"
            f"  <b>Прізвище:</b> {me.last_name if me.last_name else 'Не вказано'}\n"
            f"  <b>Username:</b> @{me.username if me.username else 'Не вказано'}\n"
            f"  <b>Телефон:</b> {me.phone if me.phone else 'Не вказано'}\n"
        )
    except Exception as e:
        user_info_text = f"Помилка при отриманні інформації про користувача Telethon: {e}"
        logger.error(f"Помилка при отриманні інформації про користувача Telethon: {e}", exc_info=True) # Додано exc_info=True

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
    telethon_manager: Any,
    state: FSMContext
) -> None:
    logger.info(f"Користувач {callback.from_user.id} запросив приєднання Telethon до каналу.")

    # Знову, отримуємо активний клієнт
    active_client = None
    if telethon_manager and telethon_manager.clients:
        first_phone = next(iter(telethon_manager.clients), None)
        if first_phone:
            active_client = telethon_manager.clients[first_phone]

    if not active_client or not active_client.is_connected():
        await callback.answer("Клієнт Telethon не підключено. Будь ласка, авторизуйтесь спочатку.", show_alert=True)
        return

    await callback.answer("Приєднання до каналу Telethon...", show_alert=True)
    await callback.message.edit_text(
        "Будь ласка, надішліть посилання або username каналу/чату, до якого потрібно приєднатися:",
        reply_markup=get_telethon_actions_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(AdminStates.waiting_for_telethon_input)
    await state.update_data(telethon_auth_step="join_channel")


@router.callback_query(
    AdminCallback.filter(F.action == "telethon_chats"), # Додано хендлер для "Чат-матриця"
    StateFilter(AdminStates.admin_main, AdminStates.telethon_management)
)
async def show_telethon_chats(
    callback: types.CallbackQuery,
    telethon_manager: Any,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув 'Чат-матриця'.")
    logger.debug(f"Telethon Manager received in show_telethon_chats: {telethon_manager}")

    await state.set_state(AdminStates.telethon_management)
    await callback.answer("Завантаження чатів. Це може зайняти деякий час...", show_alert=True)

    active_client = None
    if telethon_manager and telethon_manager.clients:
        for phone_number, client_obj in telethon_manager.clients.items():
            if client_obj.is_connected():
                active_client = client_obj
                logger.debug(f"Found active Telethon client: {phone_number}")
                break
    
    if not active_client:
        logger.warning(f"No active Telethon clients found for user {user_id}. Cannot fetch dialogs.")
        await callback.message.edit_text(
            "❌ Telethon клієнт не підключено. Будь ласка, авторизуйтесь спочатку.",
            reply_markup=get_telethon_actions_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        return

    dialogs_info = "<b>💬 Активні чати та канали:</b>\n\n"
    try:
        logger.debug(f"Calling get_dialogs() on active_client: {active_client}")
        dialogs: List[Dialog] = await active_client.get_dialogs()
        logger.debug(f"Successfully received {len(dialogs)} dialogs.")
        
        if not dialogs:
            dialogs_info += "Не знайдено жодного чату або каналу."
        else:
            # Сортуємо діалоги: спочатку канали, потім групи, потім особисті чати
            # Також можна сортувати за датою останнього повідомлення, але для простоти за типом
            
            # Обмежуємо кількість діалогів, щоб уникнути занадто довгого повідомлення
            max_dialogs_to_show = 30 
            
            for i, d in enumerate(dialogs[:max_dialogs_to_show]):
                if d.is_channel:
                    entity_type = "Канал 📣"
                elif d.is_group:
                    entity_type = "Група 👥"
                elif d.is_user:
                    entity_type = "Приватний чат 👤"
                else:
                    entity_type = "Невідомий тип"

                title = d.title if d.title else "Без назви"
                username = f"@{d.entity.username}" if hasattr(d.entity, 'username') and d.entity.username else ""
                
                dialogs_info += (
                    f"<b>{i+1}. {title}</b>\n"
                    f"  <i>Тип:</i> {entity_type}\n"
                    f"  <i>ID:</i> <code>{d.id}</code>\n"
                    f"  <i>Username:</i> {username if username else 'Немає'}\n"
                    f"  <i>Останнє повідомлення:</i> {d.date.strftime('%Y-%m-%d %H:%M:%S') if d.date else 'Невідомо'}\n\n"
                )
            
            if len(dialogs) > max_dialogs_to_show:
                dialogs_info += f"Показано перші {max_dialogs_to_show} з {len(dialogs)} чатів. Для повного списку використовуйте інший інструмент."

    except Exception as e:
        logger.error(f"Помилка при отриманні діалогів Telethon: {e}", exc_info=True) # Додано exc_info=True
        dialogs_info += f"Помилка при завантаженні діалогів: {e}"

    await callback.message.edit_text(
        dialogs_info,
        reply_markup=get_telethon_actions_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


# --- ВИПРАВЛЕНО: Хендлер для кнопки "📡 ReLink · Статус каналу зв'язку" ---
@router.callback_query(
    AdminCallback.filter(F.action == "connection_status"), # Це callback для кнопки "📡 ReLink · Статус каналу зв'язку"
    StateFilter(AdminStates.admin_main, AdminStates.telethon_management)
)
async def telethon_connection_status(
    callback: types.CallbackQuery,
    telethon_manager: Any # telethon_manager має бути переданий через Middleware
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} перевіряє статус з'єднання.")
    logger.debug(f"Telethon Manager received in telethon_connection_status: {telethon_manager}")
    
    status_message = "❌ Telethon API: не підключено або немає активних клієнтів."

    # Перевіряємо, чи є активні клієнти в менеджері
    if telethon_manager and telethon_manager.clients:
        # Проходимося по всіх зареєстрованих клієнтах
        for phone_number, client_obj in telethon_manager.clients.items():
            if client_obj.is_connected():
                status_message = f"✅ Telethon API: підключено (через {phone_number})"
                break # Знайшли підключений клієнт, можна виходити

    await callback.answer(status_message, show_alert=True)