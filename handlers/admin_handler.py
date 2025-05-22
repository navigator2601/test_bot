# handlers/admin_handler.py
import logging
import asyncio
import os

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.client.bot import Bot # Важливо: імпортуємо Bot

from keyboards.admin_keyboard import create_admin_menu_keyboard
from keyboards.inline_keyboard import create_paginated_users_keyboard, create_user_management_keyboard

from states.admin_states import AdminStates
from database.users_db import (
    get_all_users,
    update_user_status,
    get_user_data,
    update_user_access_level,
    add_new_user_manually
)
from telethon_client import (
    get_telethon_client_instance,
    disconnect_telethon_client,
    is_telethon_client_authorized,
    set_auth_callbacks
)
from config import ADMIN_ID
from handlers.start_handler import start_command # Імпортуємо start_command на початку файлу

admin_logger = logging.getLogger(__name__)
router = Router()

_telethon_fsm_context_map = {}
_telethon_auth_queues = {}

async def _telethon_code_request_aiogram_callback():
    user_id = ADMIN_ID
    if user_id in _telethon_fsm_context_map:
        state = _telethon_fsm_context_map[user_id]
        stored_data = await state.get_data()
        bot_instance_from_state = stored_data.get("bot_instance")

        if not bot_instance_from_state:
            admin_logger.error(f"Bot instance not found in FSMContext for user {user_id}. Cannot proceed with Telethon auth.")
            raise ConnectionError("Bot instance not found in FSMContext.")

        await bot_instance_from_state.send_message(user_id, "Будь ласка, введіть **код авторизації**, отриманий від Telegram:", reply_markup=ReplyKeyboardRemove())
        admin_logger.info(f"Запитано код авторизації Telethon у користувача {user_id}.")
        return await _wait_for_user_input(user_id, "code")
    else:
        admin_logger.error(f"Немає FSMContext для користувача {user_id} для запиту коду. Неможливо продовжити авторизацію Telethon.")
        raise ConnectionError("FSMContext not found for code request.")

async def _telethon_password_request_aiogram_callback():
    user_id = ADMIN_ID
    if user_id in _telethon_fsm_context_map:
        state = _telethon_fsm_context_map[user_id]
        stored_data = await state.get_data()
        bot_instance_from_state = stored_data.get("bot_instance")

        if not bot_instance_from_state:
            admin_logger.error(f"Bot instance not found in FSMContext for user {user_id}. Cannot proceed with Telethon auth.")
            raise ConnectionError("Bot instance not found in FSMContext.")

        await bot_instance_from_state.send_message(user_id, "Будь ласка, введіть **пароль двохетапної перевірки** Telegram:", reply_markup=ReplyKeyboardRemove())
        admin_logger.info(f"Запитано пароль Telethon у користувача {user_id}.")
        return await _wait_for_user_input(user_id, "password")
    else:
        admin_logger.error(f"Немає FSMContext для користувача {user_id} для запиту паролю. Неможливо продовжити авторизацію Telethon.")
        raise ConnectionError("FSMContext not found for password request.")

async def _wait_for_user_input(user_id: int, input_type: str):
    if user_id not in _telethon_auth_queues:
        _telethon_auth_queues[user_id] = asyncio.Queue()
    
    admin_logger.debug(f"Очікуємо введення '{input_type}' від користувача {user_id}...")
    user_input = await _telethon_auth_queues[user_id].get()
    admin_logger.debug(f"Отримано введення '{input_type}' від користувача {user_id}.")
    return user_input

@router.message(F.text == "⚙️ Адміністрування")
@router.message(Command("admin"))
async def admin_panel_entry(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username
    admin_logger.info(f"Користувач ID: {user_id} (@{username}) відкрив адмін-меню.")

    if user_id != ADMIN_ID:
        admin_logger.warning(f"Несанкціонована спроба доступу до адмін-панелі від користувача ID: {user_id}.")
        await message.answer("У вас немає прав доступу до адмін-панелі.")
        return

    await state.set_state(AdminStates.admin_panel)
    
    # Зберігаємо об'єкт bot у FSMContext для використання в колбеках Telethon
    await state.update_data(bot_instance=bot) 
    
    _telethon_fsm_context_map[user_id] = state 
    
    set_auth_callbacks(
        lambda: _telethon_code_request_aiogram_callback(),
        lambda: _telethon_password_request_aiogram_callback()
    )

    await message.answer("Ласкаво просимо до адмін-панелі!", reply_markup=create_admin_menu_keyboard())

@router.message(F.text == "🚀 Авторизувати Telethon", AdminStates.admin_panel)
async def handle_auth_telethon_button_reply(message: Message, state: FSMContext):
    user_id = message.from_user.id
    admin_logger.info(f"Користувач ID: {user_id} натиснув '🚀 Авторизувати Telethon'.")

    await message.answer("Запускаю процес авторизації Telethon. Це може зайняти деякий час. Очікуйте запиту на введення коду або паролю.", reply_markup=ReplyKeyboardRemove())

    client = await get_telethon_client_instance()

    if client and await client.is_user_authorized():
        await message.answer("✅ Telethon клієнт успішно авторизований!", reply_markup=create_admin_menu_keyboard())
    else:
        if client is None:
            await message.answer("❌ Не вдалося авторизувати Telethon клієнт. Перевірте логи бота для детальної інформації.", reply_markup=create_admin_menu_keyboard())
        current_state = await state.get_state()
        if current_state not in [AdminStates.waiting_for_telethon_code, AdminStates.waiting_for_telethon_password]:
            await message.answer("Авторизація не завершена. Можливо, потрібен додатковий ввід.", reply_markup=create_admin_menu_keyboard())

    current_state = await state.get_state()
    if current_state not in [AdminStates.waiting_for_telethon_code, AdminStates.waiting_for_telethon_password]:
        await state.set_state(AdminStates.admin_panel)

@router.message(AdminStates.waiting_for_telethon_code)
async def process_telethon_code(message: Message, state: FSMContext):
    user_id = message.from_user.id
    code = message.text.strip()
    admin_logger.info(f"Користувач {user_id} ввів код Telethon.")

    if user_id in _telethon_auth_queues:
        await _telethon_auth_queues[user_id].put(code)
        await message.answer("Дякую за код. Перевіряю...")
    else:
        admin_logger.error(f"Немає черги для користувача {user_id} для передачі коду Telethon. Стан: {await state.get_state()}")
        await message.answer("Виникла помилка під час обробки коду. Спробуйте авторизувати Telethon знову.", reply_markup=create_admin_menu_keyboard())
        await state.set_state(AdminStates.admin_panel)

@router.message(AdminStates.waiting_for_telethon_password)
async def process_telethon_password(message: Message, state: FSMContext):
    user_id = message.from_user.id
    password = message.text.strip()
    admin_logger.info(f"Користувач {user_id} ввів пароль Telethon.")

    if user_id in _telethon_auth_queues:
        await _telethon_auth_queues[user_id].put(password)
        await message.answer("Дякую за пароль. Завершую авторизацію...")
    else:
        admin_logger.error(f"Немає черги для користувача {user_id} для передачі паролю Telethon. Стан: {await state.get_state()}")
        await message.answer("Виникла помилка під час обробки паролю. Спробуйте авторизувати Telethon знову.", reply_markup=create_admin_menu_keyboard())
        await state.set_state(AdminStates.admin_panel)

@router.message(F.text == "📊 Статус підключення", AdminStates.admin_panel)
async def handle_check_telethon_status(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    admin_logger.info(f"Користувач ID: {user_id} (@{username}) натиснув 'Статус підключення Telethon'.")

    if user_id != ADMIN_ID:
        await message.answer("У вас немає прав для виконання цієї дії.")
        return

    is_authorized = await is_telethon_client_authorized()
    if is_authorized:
        status_message = "✅ Telethon клієнт успішно авторизований і підключений!"
    else:
        status_message = "❌ Telethon клієнт не ініціалізовано або не авторизовано. Натисніть '🚀 Авторизувати Telethon', щоб розпочати процес."
    
    await message.answer(f"Статус Telethon клієнта:\n{status_message}", reply_markup=create_admin_menu_keyboard())
    await state.set_state(AdminStates.admin_panel)

@router.message(F.text == "↩️ Головне меню", AdminStates.admin_panel)
async def exit_admin_panel(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    admin_logger.info(f"Користувач ID: {user_id} вийшов з адмін-панелі.")
    await state.clear()
    # Важливо: відправляємо головну клавіатуру користувача
    await start_command(message, state, bot) 

@router.message(F.text == "👥 Користувачі", AdminStates.admin_panel)
async def handle_users_list(message: Message, state: FSMContext):
    user_id = message.from_user.id
    admin_logger.info(f"Користувач ID: {user_id} натиснув '👥 Користувачі'.")
    
    users_data = await get_all_users()
    if not users_data:
        await message.answer("Список користувачів порожній.", reply_markup=create_admin_menu_keyboard())
        await state.set_state(AdminStates.admin_panel) # Повертаємо стан до адмін-панелі, якщо користувачів немає
        return

    await state.update_data(all_users=users_data, current_page=1)
    
    await message.answer(
        "Список користувачів:",
        reply_markup=await create_paginated_users_keyboard(users_data, 1)
    )
    await state.set_state(AdminStates.viewing_users) # Встановлюємо стан перегляду користувачів

@router.callback_query(F.data.startswith("users_page:"), AdminStates.viewing_users)
async def process_user_list_pagination(callback_query: CallbackQuery, state: FSMContext):
    page = int(callback_query.data.split(":")[1])
    data = await state.get_data()
    users_data = data.get("all_users")

    if not users_data:
        await callback_query.answer("Дані користувачів не знайдено, повертаюся до адмін-панелі.")
        await state.set_state(AdminStates.admin_panel)
        await callback_query.message.delete()
        await callback_query.message.answer("Повертаюся до адмін-панелі.", reply_markup=create_admin_menu_keyboard())
        return

    await state.update_data(current_page=page)
    await callback_query.message.edit_reply_markup(reply_markup=await create_paginated_users_keyboard(users_data, page))
    await callback_query.answer()

@router.callback_query(F.data.startswith("user_select:"), AdminStates.viewing_users)
async def manage_user_access(callback_query: CallbackQuery, state: FSMContext):
    user_id_to_manage = int(callback_query.data.split(":")[1])
    admin_logger.info(f"Адміністратор {callback_query.from_user.id} обрав користувача {user_id_to_manage} для управління.")

    user_data = await get_user_data(user_id_to_manage)
    if not user_data:
        await callback_query.answer("Користувача не знайдено.")
        await state.set_state(AdminStates.admin_panel)
        await callback_query.message.delete()
        await callback_query.message.answer("Користувача не знайдено. Повертаюся до адмін-панелі.", reply_markup=create_admin_menu_keyboard())
        return

    await state.update_data(current_managed_user_id=user_id_to_manage)
    
    status_text = "Авторизований" if user_data['is_authorized'] else "НЕ авторизований"
    access_level_text = user_data['access_level']
    username_text = user_data.get('username', 'N/A')

    message_text = (
        f"Управління користувачем:\n"
        f"ID: `{user_id_to_manage}`\n"
        f"Username: @{username_text}\n"
        f"Статус: {status_text}\n"
        f"Рівень доступу: {access_level_text}"
    )
    
    sent_message = await callback_query.message.edit_text(
        message_text,
        reply_markup=await create_user_management_keyboard(user_id_to_manage)
    )
    await state.update_data(user_management_message_id=sent_message.message_id)

    await state.set_state(AdminStates.managing_user_access)
    await callback_query.answer()

@router.callback_query(F.data.startswith("authorize_user:") | F.data.startswith("deauthorize_user:"), AdminStates.managing_user_access)
async def toggle_user_authorization(callback_query: CallbackQuery, state: FSMContext):
    action = callback_query.data.split(":")[0]
    user_id_to_manage = int(callback_query.data.split(":")[1])
    
    data = await state.get_data()
    if user_id_to_manage != data.get("current_managed_user_id"):
        await callback_query.answer("Помилка: Невірний користувач. Спробуйте ще раз.")
        return

    current_user_data = await get_user_data(user_id_to_manage)
    if not current_user_data:
        await callback_query.answer("Користувача не знайдено.")
        await state.set_state(AdminStates.admin_panel)
        await callback_query.message.delete()
        await callback_query.message.answer("Користувача не знайдено. Повертаюся до адмін-панелі.", reply_markup=create_admin_menu_keyboard())
        return

    new_status = (action == "authorize_user")

    if current_user_data['is_authorized'] == new_status:
        await callback_query.answer(f"Користувач вже {'авторизований' if new_status else 'не авторизований'}.")
        return

    success = await update_user_status(user_id_to_manage, new_status)

    if success:
        await callback_query.answer(f"Статус змінено на {'авторизований' if new_status else 'не авторизований'}.")
        updated_user_data = await get_user_data(user_id_to_manage)
        status_text = "Авторизований" if updated_user_data['is_authorized'] else "НЕ авторизований"
        access_level_text = updated_user_data['access_level']
        username_text = updated_user_data.get('username', 'N/A')

        message_text = (
            f"Управління користувачем:\n"
            f"ID: `{user_id_to_manage}`\n"
            f"Username: @{username_text}\n"
            f"Статус: {status_text}\n"
            f"Рівень доступу: {access_level_text}"
        )
        await callback_query.message.edit_text(
            message_text,
            reply_markup=await create_user_management_keyboard(user_id_to_manage)
        )
    else:
        await callback_query.answer("Помилка при зміні статусу.")

@router.callback_query(F.data.startswith("change_access:"), AdminStates.managing_user_access)
async def prompt_change_access_level(callback_query: CallbackQuery, state: FSMContext):
    user_id_to_manage = int(callback_query.data.split(":")[1])
    
    await state.update_data(current_managed_user_id=user_id_to_manage)
    
    await state.update_data(user_management_message_id=callback_query.message.message_id)

    await callback_query.message.edit_text(
        f"Введіть новий рівень доступу (ціле число від 0 до 10) для користувача ID: `{user_id_to_manage}`.",
        reply_markup=None
    )
    await callback_query.answer()
    await state.set_state(AdminStates.waiting_for_access_level)

@router.message(AdminStates.waiting_for_access_level)
async def process_new_access_level(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    data = await state.get_data()
    user_id_to_manage = data.get("current_managed_user_id")
    user_management_message_id = data.get("user_management_message_id")

    if user_id_to_manage is None:
        await message.answer("Помилка: Користувач для управління не вибраний. Повертаюся до адмін-панелі.", reply_markup=create_admin_menu_keyboard())
        await state.set_state(AdminStates.admin_panel)
        return

    try:
        new_access_level = int(message.text)
        if not (0 <= new_access_level <= 10):
            raise ValueError("Рівень доступу повинен бути числом від 0 до 10.")
    except ValueError:
        await message.answer("Некоректний рівень доступу. Будь ласка, введіть ціле число від 0 до 10.", reply_markup=None)
        return

    current_user_data = await get_user_data(user_id_to_manage)
    
    if current_user_data and current_user_data['access_level'] == new_access_level:
        await message.reply(f"Рівень доступу для користувача ID: `{user_id_to_manage}` вже встановлено на {new_access_level}.")
        
        if user_management_message_id:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_management_message_id,
                text=(
                    f"Управління користувачем:\n"
                    f"ID: `{user_id_to_manage}`\n"
                    f"Username: @{current_user_data.get('username', 'N/A')}\n"
                    f"Статус: {'Авторизований' if current_user_data['is_authorized'] else 'НЕ авторизований'}\n"
                    f"Рівень доступу: {current_user_data['access_level']}"
                ),
                reply_markup=await create_user_management_keyboard(user_id_to_manage)
            )
        else:
            await message.answer(
                f"Управління користувачем:\n"
                f"ID: `{user_id_to_manage}`\n"
                f"Username: @{current_user_data.get('username', 'N/A')}\n"
                f"Статус: {'Авторизований' if current_user_data['is_authorized'] else 'НЕ авторизований'}\n"
                f"Рівень доступу: {current_user_data['access_level']}",
                reply_markup=await create_user_management_keyboard(user_id_to_manage)
            )

        await state.set_state(AdminStates.managing_user_access)
        return

    success = await update_user_access_level(user_id_to_manage, new_access_level)

    if success:
        await message.reply(f"Рівень доступу для користувача ID: `{user_id_to_manage}` оновлено на {new_access_level}.")
        
        user_data = await get_user_data(user_id_to_manage)
        status_text = "Авторизований" if user_data['is_authorized'] else "НЕ авторизований"
        username_text = user_data.get('username', 'N/A')
        message_text = (
            f"Управління користувачем:\n"
            f"ID: `{user_id_to_manage}`\n"
            f"Username: @{username_text}\n"
            f"Статус: {status_text}\n"
            f"Рівень доступу: {new_access_level}"
        )
        
        if user_management_message_id:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=user_management_message_id,
                text=message_text,
                reply_markup=await create_user_management_keyboard(user_id_to_manage)
            )
        else:
            await message.answer(
                message_text,
                reply_markup=await create_user_management_keyboard(user_id_to_manage)
            )
        
        await state.set_state(AdminStates.managing_user_access)

    else:
        await message.answer("Помилка при оновленні рівня доступу. Спробуйте ще раз.", reply_markup=create_admin_menu_keyboard())
        await state.set_state(AdminStates.admin_panel)

@router.callback_query(F.data == "back_to_users_list", AdminStates.managing_user_access)
async def back_to_users_list(callback_query: CallbackQuery, state: FSMContext):
    admin_logger.info(f"Адміністратор {callback_query.from_user.id} повернувся до списку користувачів.")
    data = await state.get_data()
    users_data = data.get("all_users")
    current_page = data.get("current_page", 1)

    if not users_data:
        await callback_query.answer("Дані користувачів не знайдено, повертаюся до адмін-панелі.")
        await state.set_state(AdminStates.admin_panel)
        await callback_query.message.delete()
        await callback_query.message.answer("Повертаюся до адмін-панелі.", reply_markup=create_admin_menu_keyboard())
        return

    await callback_query.message.edit_text(
        "Список користувачів:",
        reply_markup=await create_paginated_users_keyboard(users_data, current_page)
    )
    await state.set_state(AdminStates.viewing_users)
    await callback_query.answer()

@router.callback_query(F.data == "back_to_admin_panel", AdminStates.viewing_users)
async def back_to_admin_panel_from_users(callback_query: CallbackQuery, state: FSMContext):
    admin_logger.info(f"Адміністратор {callback_query.from_user.id} повернувся до адмін-панелі зі списку користувачів.")
    await state.set_state(AdminStates.admin_panel)
    await callback_query.message.delete()
    await callback_query.message.answer("Повертаюся до адмін-панелі.", reply_markup=create_admin_menu_keyboard())
    await callback_query.answer()

@router.callback_query(F.data == "close_menu")
async def close_message_and_menu(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    admin_logger.info(f"Користувач ID: {user_id} натиснув 'Закрити' інлайн-клавіатуру. Видаляю повідомлення.")
    await callback_query.message.delete()
    await state.set_state(AdminStates.admin_panel) # Повертаємо стан
    await callback_query.answer("Повідомлення закрито. Повернуто до адмін-панелі.")
    # Обов'язково надсилаємо головне меню адміна після закриття інлайн-клавіатури
    await callback_query.message.answer("Повертаюся до адмін-панелі.", reply_markup=create_admin_menu_keyboard())


@router.message(F.text == "➕ Додати нового користувача", AdminStates.admin_panel)
async def add_new_user_manually_prompt(message: Message, state: FSMContext):
    user_id = message.from_user.id
    admin_logger.info(f"Користувач ID: {user_id} натиснув '➕ Додати нового користувача'.")
    await state.set_state(AdminStates.waiting_for_user_id_to_add)
    await message.answer("Будь ласка, введіть **ID користувача Telegram**, якого ви хочете додати вручну (наприклад, 123456789):", reply_markup=ReplyKeyboardRemove())

@router.message(AdminStates.waiting_for_user_id_to_add)
async def process_user_id_to_add(message: Message, state: FSMContext):
    user_id_admin = message.from_user.id
    try:
        new_user_id = int(message.text.strip())
        if new_user_id <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Будь ласка, введіть коректний числовий ID користувача.", reply_markup=None)
        return

    existing_user = await get_user_data(new_user_id)
    if existing_user:
        await message.answer(f"Користувач з ID `{new_user_id}` вже існує в базі даних.", reply_markup=create_admin_menu_keyboard())
        admin_logger.warning(f"Адміністратор {user_id_admin} спробував додати існуючого користувача: {new_user_id}.")
        await state.set_state(AdminStates.admin_panel)
        return

    success = await add_new_user_manually(new_user_id, is_authorized=True, access_level=0)

    if success:
        admin_logger.info(f"Адміністратор {user_id_admin} успішно додав користувача з ID: {new_user_id}.")
        await message.answer(f"Користувач з ID `{new_user_id}` успішно доданий до бази даних.\n"
                             f"Він авторизований і має базовий рівень доступу (0).", reply_markup=create_admin_menu_keyboard())
    else:
        admin_logger.error(f"Адміністратор {user_id_admin} не зміг додати користувача з ID: {new_user_id}.")
        await message.answer("Не вдалося додати користувача. Перевірте логи або спробуйте ще раз.", reply_markup=create_admin_menu_keyboard())

    await state.set_state(AdminStates.admin_panel)

@router.message(F.text == "📝 Подивитися логи", AdminStates.admin_panel)
async def view_logs_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    admin_logger.info(f"Користувач ID: {user_id} натиснув '📝 Подивитися логи'.")

    if user_id != ADMIN_ID:
        await message.answer("У вас немає прав доступу до логів.")
        return

    try:
        log_file_path = "bot.log"
        if os.path.exists(log_file_path):
            with open(log_file_path, "r", encoding="utf-8") as f:
                logs = f.readlines()
            
            if logs:
                recent_logs = "".join(logs[-20:])
                await message.answer(f"Останні рядки логів:\n```\n{recent_logs}\n```", parse_mode="Markdown")
            else:
                await message.answer("Лог-файл порожній.")
        else:
            await message.answer("Лог-файл не знайдено.")
    except Exception as e:
        admin_logger.error(f"Помилка при читанні лог-файлу: {e}", exc_info=True)
        await message.answer("Виникла помилка при спробі прочитати лог-файл.")
    
    await state.set_state(AdminStates.admin_panel)
    await message.answer("Повертаюся до адмін-панелі.", reply_markup=create_admin_menu_keyboard())