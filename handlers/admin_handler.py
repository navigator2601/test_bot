# handlers/admin_handler.py

import logging
from aiogram import Router, types, Bot, F
from aiogram.filters.callback_data import CallbackData
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
from keyboards.reply_keyboard import get_main_menu_keyboard # Для повернення в головне меню
from common.messages import get_access_level_description, get_random_admin_welcome_message # <--- ОНОВЛЕНО ІМПОРТИ
from common.constants import ACCESS_LEVEL_BUTTONS, BUTTONS_PER_PAGE # <--- ОНОВЛЕНО ІМПОРТИ


logger = logging.getLogger(__name__)

router = Router()

# Класи Callbacks для адмін-панелі
class AdminCallback(CallbackData, prefix="admin"):
    action: str
    user_id: Optional[int] = None
    page: Optional[int] = 0
    level: Optional[int] = None

class UserActionCallback(CallbackData, prefix="user_action"):
    action: str # authorize, unauthorize, change_level
    user_id: int

class AccessLevelCallback(CallbackData, prefix="access_level"):
    level: int
    user_id: int

# СТАНИ FSM ДЛЯ АДМІН-ПАНЕЛІ
class AdminStates(StatesGroup):
    admin_main = State() # Головна адмін-панель
    user_management = State() # Управління користувачами
    confirm_action = State() # Підтвердження дії
    set_access_level = State() # Встановлення рівня доступу
    telethon_management = State() # Управління Telethon

# ACCESS_LEVEL_BUTTONS БІЛЬШЕ НЕ ПОТРІБЕН І ЙОГО СЛІД ВИДАЛИТИ З ЦЬОГО ФАЙЛУ!

# Функція для отримання інформації про користувача (щоб уникнути дублювання коду)
async def _get_user_info_message(db_pool: asyncpg.Pool, user_id: int) -> str:
    user = await users_db.get_user(db_pool, user_id)
    if not user:
        return f"Користувача з ID {user_id} не знайдено."

    user_info_parts = [
        f"<b>⚙️ Інформація про користувача (ID: <code>{user.get('id')}</code>):</b>",
        f"Ім'я: <b>{user.get('first_name', 'Не вказано')}</b>",
        f"Прізвище: <b>{user.get('last_name', 'Не вказано')}</b>",
        f"Username: <b>@{user.get('username', 'Не вказано')}</b>",
        f"Рівень доступу: <b>{user.get('access_level', 0)}</b>"
    ]
    is_authorized_text = "✅ Авторизований" if user.get('is_authorized', False) else "❌ Неавторизований"
    user_info_parts.append(f"Статус авторизації: {is_authorized_text}")
    user_info_parts.append(f"Дата реєстрації: {user.get('registration_date', 'N/A').strftime('%Y-%m-%d %H:%M:%S')}")
    user_info_parts.append(f"Остання активність: {user.get('last_activity', 'N/A').strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(user_info_parts)


@router.callback_query(AdminCallback.filter(F.action == "show_users"), AdminStates.admin_main | AdminStates.user_management)
async def show_users_list(
    callback: types.CallbackQuery,
    callback_data: AdminCallback,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) натиснув 'show_users_list'.")

    await state.set_state(AdminStates.user_management)

    current_page = callback_data.page
    if current_page is None: # На випадок прямого виклику без page
        current_page = 0
    
    users = await users_db.get_all_users(db_pool)
    users.sort(key=lambda u: u.get('id', 0)) # Сортуємо за ID для стабільної пагінації

    keyboard = get_users_list_keyboard(users, current_page, BUTTONS_PER_PAGE) # Використовуємо BUTTONS_PER_PAGE з common.constants

    await callback.message.edit_text(
        "<b>👥 Юзер-матриця:</b>\n\nСписок користувачів системи:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()
    logger.info(f"Користувачу {user_id} показано список користувачів (сторінка {current_page + 1}).")

# Обробка пагінації для списку користувачів
@router.callback_query(AdminCallback.filter(F.action == "users_page"), AdminStates.user_management)
async def process_users_pagination(
    callback: types.CallbackQuery,
    callback_data: AdminCallback,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    await show_users_list(callback, callback_data, db_pool, state)
    await callback.answer()

@router.callback_query(F.data.startswith("user_"), AdminStates.user_management)
async def process_user_selection(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name
    selected_user_id = int(callback.data.split('_')[1])
    logger.info(f"Користувач {user_name} (ID: {user_id}) вибрав користувача {selected_user_id} для управління.")

    user_to_manage = await users_db.get_user(db_pool, selected_user_id)
    if not user_to_manage:
        await callback.message.edit_text("Користувача не знайдено.")
        await callback.answer()
        return

    is_authorized = user_to_manage.get('is_authorized', False)
    current_access_level = user_to_manage.get('access_level', 0)

    user_info_message = await _get_user_info_message(db_pool, selected_user_id) # Використовуємо хелпер
    keyboard = get_user_actions_keyboard(is_authorized, current_access_level, selected_user_id)

    await state.update_data(selected_user_id=selected_user_id) # Зберігаємо ID обраного користувача в стані
    await callback.message.edit_text(user_info_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(UserActionCallback.filter(F.action.in_({"authorize", "unauthorize"})), AdminStates.user_management)
async def process_authorize_unauthorize(
    callback: types.CallbackQuery,
    callback_data: UserActionCallback,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    selected_user_id = callback_data.user_id
    action_type = callback_data.action # 'authorize' або 'unauthorize'
    
    logger.info(f"Користувач {user_id} ініціював {action_type} для користувача {selected_user_id}.")

    current_state_data = await state.get_data()
    stored_selected_user_id = current_state_data.get('selected_user_id')

    if stored_selected_user_id != selected_user_id:
        logger.warning(f"Невідповідність user_id: {stored_selected_user_id} (state) != {selected_user_id} (callback_data).")
        await callback.answer("Помилка: Вибраний користувач не відповідає поточному стану.", show_alert=True)
        return

    action_text = "авторизацію" if action_type == "authorize" else "деавторизацію"
    confirm_message = f"Ви впевнені, що хочете виконати {action_text} користувача з ID <code>{selected_user_id}</code>?"
    
    # Зберігаємо дію для підтвердження
    await state.update_data(pending_action={'type': action_type, 'user_id': selected_user_id})
    keyboard = get_confirm_action_keyboard(f"{action_type}_{selected_user_id}")
    
    await callback.message.edit_text(confirm_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await state.set_state(AdminStates.confirm_action)
    await callback.answer()


@router.callback_query(AccessLevelCallback.filter(), AdminStates.set_access_level)
async def process_set_access_level(
    callback: types.CallbackQuery,
    callback_data: AccessLevelCallback,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    selected_user_id = callback_data.user_id
    new_access_level = callback_data.level
    
    logger.info(f"Користувач {user_id} спробував встановити рівень доступу {new_access_level} для користувача {selected_user_id}.")

    # Отримуємо інформацію про поточного адміна, щоб перевірити його рівень доступу
    admin_access_level = await users_db.get_user_access_level(db_pool, user_id)
    if admin_access_level is None or admin_access_level < 10:
        await callback.answer("У вас недостатньо прав для виконання цієї дії.", show_alert=True)
        logger.warning(f"Неавторизована спроба зміни рівня доступу користувачем {user_id} для {selected_user_id}.")
        # Можна повернути до попереднього стану, але, ймовірно, краще дозволити користувачу просто залишитись
        # у поточному меню або повернутися до головного адмін-меню.
        await state.set_state(AdminStates.user_management) # Повертаємося до управління користувачами
        await callback.message.edit_text(
            "У вас недостатньо прав. Дія скасована.",
            reply_markup=get_user_actions_keyboard(
                await users_db.is_user_authorized(db_pool, selected_user_id),
                (await users_db.get_user(db_pool, selected_user_id)).get('access_level', 0),
                selected_user_id
            ),
            parse_mode=ParseMode.HTML
        )
        return

    # Перевірка, чи не намагається адміністратор понизити або підвищити себе або іншого адміна вищого рівня
    if selected_user_id == user_id and new_access_level > admin_access_level:
        await callback.answer("Ви не можете підвищити свій власний рівень доступу таким чином.", show_alert=True)
        logger.warning(f"Користувач {user_id} спробував підвищити свій рівень доступу.")
        # Повертаємо до меню вибору рівня, щоб користувач міг вибрати інший рівень або скасувати
        await callback.message.edit_text(
            "Ви не можете підвищити свій рівень доступу таким чином.",
            reply_markup=get_access_level_keyboard(selected_user_id),
            parse_mode=ParseMode.HTML
        )
        return
    
    target_user_current_level = (await users_db.get_user(db_pool, selected_user_id)).get('access_level', 0)
    if admin_access_level <= target_user_current_level and selected_user_id != user_id:
        await callback.answer("Ви не можете змінювати рівень доступу користувача з рівнем, рівним або вищим за ваш.", show_alert=True)
        logger.warning(f"Користувач {user_id} спробував змінити рівень доступу користувача {selected_user_id} з рівнем {target_user_current_level}, який більший або дорівнює його власному {admin_access_level}.")
        # Повертаємо до меню вибору рівня
        await callback.message.edit_text(
            "Ви не можете змінювати рівень доступу користувача з рівнем, рівним або вищим за ваш.",
            reply_markup=get_access_level_keyboard(selected_user_id),
            parse_mode=ParseMode.HTML
        )
        return

    # Зберігаємо дію для підтвердження
    await state.update_data(pending_action={'type': 'set_access_level', 'user_id': selected_user_id, 'level': new_access_level})
    
    level_name = next((name for level, name in ACCESS_LEVEL_BUTTONS if level == new_access_level), f"Рівень {new_access_level}")
    confirm_message = (
        f"Ви впевнені, що хочете встановити рівень доступу "
        f"<b>{level_name} ({new_access_level})</b> для користувача з ID <code>{selected_user_id}</code>?"
    )
    keyboard = get_confirm_action_keyboard(f"set_access_level_{new_access_level}_{selected_user_id}")
    
    await callback.message.edit_text(confirm_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await state.set_state(AdminStates.confirm_action)
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_"), AdminStates.confirm_action)
async def process_confirm_action(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    action_full_data = callback.data.split('confirm_')[1]
    
    current_state_data = await state.get_data()
    pending_action = current_state_data.get('pending_action')

    if not pending_action:
        logger.error(f"Користувач {user_id} спробував підтвердити дію, але pending_action не знайдено.")
        await callback.answer("Помилка: Немає дії для підтвердження.", show_alert=True)
        await state.set_state(AdminStates.user_management) # Повертаємося до управління користувачами
        await callback.message.edit_text("Дія скасована через помилку. Ви повернулись до списку користувачів.", reply_markup=get_admin_main_keyboard(), parse_mode=ParseMode.HTML)
        return

    action_type = pending_action['type']
    selected_user_id = pending_action['user_id']
    
    success_message = "Дія успішно виконана."
    error_message = "Виникла помилка під час виконання дії."
    
    try:
        if action_type == "authorize":
            await users_db.set_user_authorization_status(db_pool, selected_user_id, True)
            success_message = f"Користувач <code>{selected_user_id}</code> успішно авторизований."
            logger.info(f"Користувач {user_id} авторизував користувача {selected_user_id}.")
        elif action_type == "unauthorize":
            await users_db.set_user_authorization_status(db_pool, selected_user_id, False)
            success_message = f"Користувач <code>{selected_user_id}</code> успішно деавторизований."
            logger.info(f"Користувач {user_id} деавторизував користувача {selected_user_id}.")
        elif action_type == "set_access_level":
            new_access_level = pending_action['level']
            await users_db.set_user_access_level(db_pool, selected_user_id, new_access_level)
            level_name = next((name for level, name in ACCESS_LEVEL_BUTTONS if level == new_access_level), f"Рівень {new_access_level}")
            success_message = (
                f"Рівень доступу користувача <code>{selected_user_id}</code> успішно встановлено на "
                f"<b>{level_name} ({new_access_level})</b>."
            )
            logger.info(f"Користувач {user_id} встановив рівень доступу {new_access_level} для користувача {selected_user_id}.")
        else:
            await callback.answer("Невідома дія.", show_alert=True)
            logger.warning(f"Невідома дія підтвердження: {action_type}.")
            await state.set_state(AdminStates.user_management) # Повертаємося до управління користувачами
            await callback.message.edit_text("Дія скасована. Ви повернулись до списку користувачів.", reply_markup=get_admin_main_keyboard(), parse_mode=ParseMode.HTML)
            return

        await callback.message.edit_text(success_message, parse_mode=ParseMode.HTML)
        
        # Повертаємось до меню управління користувачем або до списку користувачів
        await state.set_state(AdminStates.user_management) # Переходимо в стан управління користувачами
        user_info_message = await _get_user_info_message(db_pool, selected_user_id)
        is_authorized_after_action = await users_db.is_user_authorized(db_pool, selected_user_id)
        current_access_level_after_action = (await users_db.get_user(db_pool, selected_user_id)).get('access_level', 0)
        keyboard = get_user_actions_keyboard(is_authorized_after_action, current_access_level_after_action, selected_user_id)
        await callback.message.answer(user_info_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Помилка при підтвердженні дії '{action_type}' для користувача {selected_user_id}: {e}", exc_info=True)
        await callback.message.edit_text(error_message, parse_mode=ParseMode.HTML)
        await state.set_state(AdminStates.user_management) # Повертаємось до управління користувачами
        user_info_message = await _get_user_info_message(db_pool, selected_user_id)
        is_authorized_after_action = await users_db.is_user_authorized(db_pool, selected_user_id)
        current_access_level_after_action = (await users_db.get_user(db_pool, selected_user_id)).get('access_level', 0)
        keyboard = get_user_actions_keyboard(is_authorized_after_action, current_access_level_after_action, selected_user_id)
        await callback.message.answer(user_info_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    await callback.answer()


@router.callback_query(F.data == "cancel_action", AdminStates.confirm_action)
async def process_cancel_action(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} скасував дію.")

    current_state_data = await state.get_data()
    pending_action = current_state_data.get('pending_action')
    
    if pending_action and 'user_id' in pending_action:
        selected_user_id = pending_action['user_id']
        await state.set_state(AdminStates.user_management) # Повертаємося до управління користувачами
        user_info_message = await _get_user_info_message(db_pool, selected_user_id)
        is_authorized_after_action = await users_db.is_user_authorized(db_pool, selected_user_id)
        current_access_level_after_action = (await users_db.get_user(db_pool, selected_user_id)).get('access_level', 0)
        keyboard = get_user_actions_keyboard(is_authorized_after_action, current_access_level_after_action, selected_user_id)
        await callback.message.edit_text("Дія скасована.", reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        # Якщо немає конкретного користувача або pending_action невірний, повертаємо до головної адмін-панелі
        await state.set_state(AdminStates.admin_main)
        await callback.message.edit_text(
            "Дія скасована. Ви повернулись до головної адмін-панелі.",
            reply_markup=get_admin_main_keyboard(),
            parse_mode=ParseMode.HTML
        )
    
    await state.update_data(pending_action=None) # Очищаємо pending_action
    await callback.answer("Дія скасована.")


@router.callback_query(F.data.startswith("change_access_level_"), AdminStates.user_management)
async def process_change_access_level_button(
    callback: types.CallbackQuery,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    selected_user_id = int(callback.data.split('_')[3])
    logger.info(f"Користувач {user_id} ініціював зміну рівня доступу для користувача {selected_user_id}.")

    await state.set_state(AdminStates.set_access_level)
    await state.update_data(selected_user_id=selected_user_id) # Зберігаємо ID обраного користувача

    keyboard = get_access_level_keyboard(selected_user_id) # Передаємо selected_user_id для кнопки "Скасувати"
    await callback.message.edit_text(
        f"Виберіть новий рівень доступу для користувача з ID <code>{selected_user_id}</code>:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(AdminCallback.filter(F.action == "telethon_auth"), AdminStates.admin_main | AdminStates.telethon_management)
async def process_telethon_auth(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув 'TeleKey · Авторизація API-зв’язку'.")
    
    await state.set_state(AdminStates.telethon_management) # Встановлюємо стан для Telethon управління

    keyboard = get_telethon_actions_keyboard()
    await callback.message.edit_text(
        "<b>🔐 TeleKey · Авторизація API-зв’язку:</b>\n\n"
        "Оберіть дію для управління Telethon API:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_admin_action", AdminStates.user_management | AdminStates.telethon_management | AdminStates.set_access_level)
async def cancel_admin_action(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext,
    bot: Bot # Потрібен, якщо send_message відбувається не через callback.message
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} скасував адмін-дію і повертається до головного адмін-меню.")
    
    await state.set_state(AdminStates.admin_main) # Повертаємось до головної адмін-панелі
    await state.update_data(pending_action=None, selected_user_id=None) # Очищаємо дані

    await callback.message.edit_text(
        "Ви повернулись до головної адмін-панелі.",
        reply_markup=get_admin_main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@router.callback_query(F.data == "close_admin_panel", AdminStates.admin_main)
async def close_admin_panel(
    callback: types.CallbackQuery,
    db_pool: asyncpg.Pool,
    state: FSMContext
) -> None:
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} закриває адмін-панель.")

    await state.clear() # Очищаємо всі стани FSM
    await state.set_state(MenuStates.main_menu) # Встановлюємо стан головного меню

    access_level = await users_db.get_user_access_level(db_pool, user_id)
    if access_level is None:
        access_level = 0
    
    # Викликаємо функцію для відображення головного меню з handlers.menu_handler
    # Це вимагає передачі message, bot, db_pool, state.
    # Оскільки тут callback, ми можемо або викликати безпосередньо send_message
    # або імітувати message для show_main_menu_handler.
    
    # Краще просто відправити повідомлення з головним меню, не викликаючи хендлер.
    await callback.message.edit_text(
        "Ви вийшли з адмін-панелі. Повернення до головного меню.",
        reply_markup=await get_main_menu_keyboard(access_level, 0), # page=0 для головного меню
        parse_mode=ParseMode.HTML
    )
    await callback.answer("Адмін-панель закрито.")
    logger.info(f"Адмін-панель закрито для користувача {user_id}.")