import logging
from typing import Any, Optional 
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telethon.tl.types import Dialog, Channel, Chat, User 

from keyboards.admin_keyboard import get_telethon_actions_keyboard, get_chat_matrix_keyboard
from common.states import AdminStates
from filters.admin_filter import AdminAccessFilter
from keyboards.callback_factories import AdminCallback

import asyncpg 

# Імпорт з оновленого файлу telethon_chats_db.py
from database.telethon_chats_db import add_telethon_allowed_chat, get_all_telethon_allowed_chats 

logger = logging.getLogger(__name__)

router = Router()

router.callback_query.filter(AdminAccessFilter())
router.message.filter(AdminAccessFilter())

# Хендлер для входу в розділ "Чат-матриця"
@router.callback_query(AdminCallback.filter(F.action == "chat_matrix"), StateFilter(AdminStates.admin_main))
async def process_chat_matrix(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув '💬 Чат-матриця'.")
    await state.set_state(AdminStates.chat_matrix_management)
    keyboard = get_chat_matrix_keyboard()
    await callback.message.edit_text(
        "<b>💬 Чат-матриця:</b>\n\nОберіть дію для управління чатами:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


# Хендлер для кнопки "📜 Список підключених чатів"
@router.callback_query(AdminCallback.filter(F.action == "list_connected_chats"), StateFilter(AdminStates.chat_matrix_management))
async def process_list_connected_chats(callback: types.CallbackQuery, db_pool: asyncpg.Pool):
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} запитав список підключених чатів.")

    chats = await get_all_telethon_allowed_chats(db_pool) # Використовуємо нову функцію

    if not chats:
        await callback.answer("Наразі немає підключених чатів.", show_alert=True)
        return

    response_text = "<b>📜 Список підключених чатів:</b>\n\n"
    for chat in chats:
        response_text += (
            f"▪️ {chat['chat_title']} (ID: <code>{chat['chat_id']}</code>) "
            f"[{chat['chat_type'].capitalize() if chat['chat_type'] else 'Невідомо'}] "
            f"{f'@{chat["username"]}' if chat['username'] else ''}\n"
        )
    
    keyboard = get_chat_matrix_keyboard() # Повертаємось до клавіатури чат-матриці

    await callback.message.edit_text(
        response_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# Хендлер для кнопки "🔍 Пошук чатів"
@router.callback_query(AdminCallback.filter(F.action == "search_chats"), StateFilter(AdminStates.chat_matrix_management))
async def process_search_chats(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} натиснув '🔍 Пошук чатів'.")
    await state.set_state(AdminStates.waiting_for_telethon_input) # Змінюємо стан для очікування вводу
    await state.update_data(telethon_auth_step="chat_search_query") # Встановлюємо крок
    await callback.message.edit_text(
        "<b>🔍 Пошук чатів:</b>\n\nВведіть назву чату, каналу або юзернейм для пошуку:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🔙 Назад до Чат-матриці", callback_data=AdminCallback(action="chat_matrix").pack())]
        ]),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# Хендлер для кнопки "Перевірити статус Telethon 👁️"
@router.callback_query(AdminCallback.filter(F.action == "telethon_check_status"), StateFilter(AdminStates.telethon_management))
async def telethon_check_status(callback: types.CallbackQuery, telethon_manager: Any):
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} перевіряє статус Telethon.")

    status_message = "❌ Telethon API: не підключено або немає активних клієнтів."
    if telethon_manager and telethon_manager.clients:
        connected_clients = [
            phone for phone, client_obj in telethon_manager.clients.items() 
            if client_obj.is_connected()
        ]
        if connected_clients:
            status_message = "✅ Telethon API: підключено через " + ", ".join(connected_clients)
        else:
            status_message = "❌ Telethon API: є клієнти, але жоден не підключено."
    
    await callback.answer(status_message, show_alert=True)


# Хендлер для кнопки "Авторизувати Telethon 🔑"
@router.callback_query(AdminCallback.filter(F.action == "telethon_start_auth"), StateFilter(AdminStates.telethon_management))
async def telethon_start_auth(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} ініціював авторизацію Telethon.")
    
    await state.set_state(AdminStates.waiting_for_telethon_input)
    await state.update_data(telethon_auth_step="phone_number")
    
    await callback.message.edit_text(
        "<b>Авторизація Telethon:</b>\n\nБудь ласка, введіть номер телефону для авторизації (у форматі +380ХХХХХХХХХ):",
        reply_markup=get_telethon_actions_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


# Хендлер для кнопки "Отримати інфо про користувача 🆔"
@router.callback_query(AdminCallback.filter(F.action == "telethon_get_user_info"), StateFilter(AdminStates.telethon_management))
async def telethon_get_user_info(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} ініціював отримання інфо про користувача.")
    await state.set_state(AdminStates.waiting_for_telethon_input)
    await state.update_data(telethon_auth_step="get_user_info")
    await callback.message.edit_text(
        "<b>Отримати інфо про користувача:</b>\n\nВведіть ID або юзернейм користувача (наприклад, @username або 123456789):",
        reply_markup=get_telethon_actions_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# Хендлер для кнопки "Приєднатися до каналу ➕"
@router.callback_query(AdminCallback.filter(F.action == "telethon_join_channel"), StateFilter(AdminStates.telethon_management))
async def telethon_join_channel_request(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    logger.info(f"Користувач {user_id} ініціював приєднання до каналу.")
    await state.set_state(AdminStates.waiting_for_telethon_input)
    await state.update_data(telethon_auth_step="join_channel")
    await callback.message.edit_text(
        "<b>Приєднатися до каналу:</b>\n\nВведіть посилання на канал (наприклад, https://t.me/channel_username або @channel_username):",
        reply_markup=get_telethon_actions_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


# Хендлер для обробки вводу від користувача у стані waiting_for_telethon_input
@router.message(StateFilter(AdminStates.waiting_for_telethon_input))
async def handle_telethon_input(message: types.Message, state: FSMContext, telethon_manager: Any):
    user_id = message.from_user.id
    state_data = await state.get_data()
    auth_step = state_data.get("telethon_auth_step")
    user_input = message.text

    if not telethon_manager or not telethon_manager.clients:
        await message.answer(
            "Telethon клієнт не ініціалізовано або немає активних сесій. Будь ласка, спочатку авторизуйтесь.",
            reply_markup=get_telethon_actions_keyboard()
        )
        await state.set_state(AdminStates.telethon_management)
        return

    # Наразі працюємо тільки з першим клієнтом, якщо їх декілька
    # Для більш складної логіки можна дозволити адміну вибирати клієнта
    first_phone = next(iter(telethon_manager.clients), None)
    if not first_phone:
        await message.answer(
            "Немає активних сесій Telethon. Будь ласка, авторизуйтесь.",
            reply_markup=get_telethon_actions_keyboard()
        )
        await state.set_state(AdminStates.telethon_management)
        return

    active_client = telethon_manager.clients[first_phone]

    if auth_step == "phone_number":
        phone_number = user_input
        # Додайте перевірку формату номера телефону, якщо потрібно
        await state.update_data(telethon_phone_number=phone_number)
        
        try:
            # Спроба відправити код
            await active_client.send_code_request(phone_number)
            await state.update_data(telethon_auth_step="auth_code")
            await message.answer(
                f"Код авторизації відправлено на {phone_number}. Будь ласка, введіть його:",
                reply_markup=get_telethon_actions_keyboard()
            )
        except Exception as e:
            logger.error(f"Помилка при відправці коду авторизації для {phone_number}: {e}", exc_info=True)
            await message.answer(
                f"Помилка при відправці коду: {e}. Спробуйте ще раз або перевірте номер.",
                reply_markup=get_telethon_actions_keyboard()
            )
            await state.set_state(AdminStates.telethon_management)

    elif auth_step == "auth_code":
        phone_number = state_data.get("telethon_phone_number")
        auth_code = user_input
        
        try:
            # Спроба авторизуватися
            await active_client.sign_in(phone_number, auth_code)
            await message.answer(
                "✅ Авторизація успішна! Telethon клієнт підключено.",
                reply_markup=get_telethon_actions_keyboard()
            )
            await state.set_state(AdminStates.telethon_management)
        except Exception as e:
            logger.error(f"Помилка при авторизації для {phone_number} з кодом {auth_code}: {e}", exc_info=True)
            await message.answer(
                f"Помилка авторизації: {e}. Перевірте код і спробуйте ще раз.",
                reply_markup=get_telethon_actions_keyboard()
            )

    elif auth_step == "get_user_info":
        entity_id = user_input
        try:
            entity = await active_client.get_entity(entity_id)
            info_text = (
                f"<b>Інформація про об'єкт:</b>\n"
                f"Ім'я/Заголовок: {getattr(entity, 'title', getattr(entity, 'first_name', 'N/A'))}\n"
                f"ID: <code>{entity.id}</code>\n"
                f"Юзернейм: @{entity.username if hasattr(entity, 'username') else 'N/A'}\n"
                f"Тип: {type(entity).__name__}"
            )
            await message.answer(info_text, parse_mode=ParseMode.HTML, reply_markup=get_telethon_actions_keyboard())
        except Exception as e:
            logger.error(f"Помилка при отриманні інформації про сутність {entity_id}: {e}", exc_info=True)
            await message.answer(f"Помилка: не вдалося отримати інформацію про '{entity_id}'. Можливо, ID невірний або сутність не знайдена.", reply_markup=get_telethon_actions_keyboard())
        finally:
            await state.set_state(AdminStates.telethon_management)

    elif auth_step == "join_channel":
        channel_link = user_input
        try:
            await active_client(JoinChannelRequest(channel_link))
            await message.answer(
                f"✅ Успішно приєднано до каналу/чату: {channel_link}",
                reply_markup=get_telethon_actions_keyboard()
            )
        except Exception as e:
            logger.error(f"Помилка при приєднанні до каналу {channel_link}: {e}", exc_info=True)
            await message.answer(
                f"Помилка при приєднанні до каналу: {e}. Перевірте посилання.",
                reply_markup=get_telethon_actions_keyboard()
            )
        finally:
            await state.set_state(AdminStates.telethon_management)
    
    elif auth_step == "chat_search_query":
        search_query = user_input
        if not search_query or len(search_query) < 3: 
            await message.answer(
                "Будь ласка, введіть принаймні 3 символи для пошуку.",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="🔙 Назад до Чат-матриці", callback_data=AdminCallback(action="chat_matrix").pack())]
                ])
            )
            return

        logger.info(f"Користувач {user_id} ввів запит для пошуку чатів: '{search_query}'.")

        # active_client вже має бути визначений на початку функції
        if not active_client or not active_client.is_connected():
            await message.answer("Клієнт Telethon не підключено. Будь ласка, авторизуйтесь спочатку.", reply_markup=get_chat_matrix_keyboard())
            await state.set_state(AdminStates.chat_matrix_management)
            return
        
        found_chats = []
        try:
            all_dialogs = await active_client.get_dialogs()
            for d in all_dialogs:
                title = d.title if d.title else ""
                username_str = f"@{d.entity.username}" if hasattr(d.entity, 'username') and d.entity.username else ""
                
                chat_type = "unknown"
                if isinstance(d.entity, Channel):
                    chat_type = "channel"
                elif isinstance(d.entity, Chat):
                    chat_type = "group"
                elif isinstance(d.entity, User):
                    chat_type = "user"

                # Додаємо чати, які відповідають запиту. Якщо чат є Channel чи Chat, додаємо його.
                if (isinstance(d.entity, (Channel, Chat, User)) and 
                    (search_query.lower() in title.lower() or (username_str and search_query.lower() in username_str.lower()))):
                    found_chats.append({
                        "id": d.id,
                        "title": title,
                        "username": username_str.lstrip('@') if username_str else None,
                        "type": chat_type
                    })


        except Exception as e:
            logger.error(f"Помилка при пошуку чатів через Telethon: {e}", exc_info=True)
            await message.answer(f"Виникла помилка під час пошуку чатів: {e}", reply_markup=get_chat_matrix_keyboard())
            await state.set_state(AdminStates.chat_matrix_management)
            return

        if found_chats:
            response_text = "<b>Знайдені чати:</b>\n\n"
            keyboard_builder = InlineKeyboardBuilder()
            for chat_info in found_chats: # Тепер ітеруємо по словниках з інформацією про чат
                response_text += (
                    f"▪️ {chat_info['title']} (ID: <code>{chat_info['id']}</code>) "
                    f"[{chat_info['type'].capitalize()}] " 
                    f"{f'@{chat_info["username"]}' if chat_info['username'] else ''}\n" 
                )
                
                keyboard_builder.row(types.InlineKeyboardButton(
                    text=f"Додати '{chat_info['title']}' до БД", 
                    callback_data=AdminCallback(
                        action="add_chat_to_db", 
                        chat_id=chat_info['id'], 
                        chat_title=chat_info['title'],
                        chat_type=chat_info['type'],      
                        username=chat_info['username']    
                    ).pack()
                ))
            keyboard_builder.row(types.InlineKeyboardButton(text="🔙 Назад до Чат-матриці", callback_data=AdminCallback(action="chat_matrix").pack()))
            await message.answer(response_text, reply_markup=keyboard_builder.as_markup(), parse_mode=ParseMode.HTML)
        else:
            await message.answer(
                "На жаль, чатів за вашим запитом не знайдено.",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="🔙 Назад до Чат-матриці", callback_data=AdminCallback(action="chat_matrix").pack())]
                ])
            )
        await state.set_state(AdminStates.chat_matrix_management)
    else:
        await message.answer("Невідомий крок авторизації. Будь ласка, спробуйте знову.")
        await state.set_state(AdminStates.telethon_management)

# Хендлер для додавання чату до БД
@router.callback_query(AdminCallback.filter(F.action == "add_chat_to_db"))
async def add_chat_to_db(
    callback: types.CallbackQuery,
    state: FSMContext,
    db_pool: asyncpg.Pool, 
    callback_data: AdminCallback
) -> None:
    chat_id = callback_data.chat_id
    chat_title = callback_data.chat_title
    chat_type = callback_data.chat_type 
    username = callback_data.username   
    user_id = callback.from_user.id

    if chat_id is None or chat_title is None:
        logger.error(f"Відсутні дані для додавання чату: chat_id={chat_id}, chat_title={chat_title}")
        await callback.answer("Помилка: відсутні дані чату для додавання.", show_alert=True)
        await state.set_state(AdminStates.chat_matrix_management)
        await callback.message.edit_text(
            "<b>💬 Чат-матриця:</b>\n\nОберіть дію для управління чатами:",
            reply_markup=get_chat_matrix_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    logger.info(f"Користувач {user_id} запросив додати чат '{chat_title}' (ID: {chat_id}, Type: {chat_type}, Username: {username}) до 'telethon_allowed_chats'.")

    success = await add_telethon_allowed_chat(db_pool, chat_id, chat_title, chat_type, username, user_id)

    if success:
        await callback.answer(f"Чат '{chat_title}' (ID: {chat_id}) додано до дозволених чатів.", show_alert=True)
    else:
        await callback.answer(f"Помилка при додаванні чату '{chat_title}' (ID: {chat_id}). Можливо, він вже доданий або виникла інша помилка.", show_alert=True)
    
    # Після додавання, повертаємось до меню чат-матриці
    await state.set_state(AdminStates.chat_matrix_management)
    keyboard = get_chat_matrix_keyboard()
    await callback.message.edit_text(
        "<b>💬 Чат-матриця:</b>\n\nОберіть дію для управління чатами:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )