# handlers/admin/chat_matrix_handlers.py
import logging
from typing import Optional # Додано імпорт Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

# Оновлені імпорти клавіатур
from keyboards.admin_keyboard import (
    get_admin_main_keyboard,
    get_chat_matrix_keyboard,
    get_search_results_keyboard,
    get_allowed_chats_list_keyboard # Додано імпорт нової клавіатури для списку дозволених чатів
)
# Оновлений імпорт фабрик колбеків
from keyboards.callback_factories import AdminCallback, ChatListCallback, ChatInfoCallback

from database.telethon_chats_db import add_telethon_allowed_chat, get_all_telethon_allowed_chats, get_telethon_allowed_chat_by_id, delete_telethon_allowed_chat

from common.states import AdminStates
from telegram_client_module.telethon_client import TelethonClientManager
from database.db_pool_manager import get_db_pool

logger = logging.getLogger(__name__)

router = Router()

# -----------------------------------------------------------
# Chat Matrix Menu
# -----------------------------------------------------------

@router.callback_query(AdminCallback.filter(F.action == "chat_matrix"))
async def show_chat_matrix_menu(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f"Користувач {callback_query.from_user.id} натиснув '💬 Чат-матриця' (вхід в меню).")
    await state.clear() # Скидаємо стан при вході в меню чат-матриці
    await callback_query.message.edit_text(
        "**⚙️ Меню Чат-матриці:**\nОберіть дію:",
        reply_markup=get_chat_matrix_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

# -----------------------------------------------------------
# Search Chats
# -----------------------------------------------------------

@router.callback_query(AdminCallback.filter(F.action == "search_chats_admin"))
async def ask_for_chat_search_query(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f"Користувач {callback_query.from_user.id} натиснув 'Пошук чатів' або повернувся до нього.")
    await callback_query.message.edit_text("Введіть назву чату для пошуку:")
    await state.set_state(AdminStates.waiting_for_chat_search_query)
    await callback_query.answer()


@router.message(AdminStates.waiting_for_chat_search_query)
async def process_chat_search_query(message: Message, state: FSMContext, telethon_manager: TelethonClientManager):
    chat_query = message.text

    active_clients = telethon_manager.get_all_active_clients()

    if not active_clients:
        await message.answer("Наразі немає активних Telethon клієнтів для виконання пошуку.")
        await state.clear()
        return

    telethon_client = next(iter(active_clients.values()))

    if not telethon_client or not telethon_client.is_connected() or not await telethon_client.is_user_authorized():
        await message.answer("Активний Telethon клієнт не підключений або не авторизований. Будь ласка, перевірте статус клієнта.")
        await state.clear()
        return

    logger.info(f"Користувач {message.from_user.id} надіслав пошуковий запит для чату: '{chat_query}'. Використовується клієнт: {list(active_clients.keys())[0]}")

    await message.answer(f"Шукаю чати за запитом '{chat_query}'...")

    try:
        found_chats = []
        
        db_pool = await get_db_pool()
        existing_allowed_chats = await get_all_telethon_allowed_chats(db_pool)
        existing_chat_ids = {chat['chat_id'] for chat in existing_allowed_chats}

        async for d in telethon_client.iter_dialogs():
            if d.is_group or d.is_channel:
                if chat_query.lower() in d.title.lower():
                    found_chats.append({
                        'chat_id': d.id,
                        'chat_title': d.title,
                        'is_added': d.id in existing_chat_ids
                    })

        if found_chats:
            await message.answer(
                "Знайдено чати:",
                reply_markup=get_search_results_keyboard(found_chats)
            )
        else:
            await message.answer("Чати не знайдено.", reply_markup=get_chat_matrix_keyboard()) # Повертаємо до меню чат-матриці
            

    except Exception as e:
        logger.error(f"Помилка пошуку чатів через Telethon клієнта: {e}", exc_info=True)
        await message.answer(f"Виникла помилка під час пошуку чатів: {e}. Можливо, клієнт не має доступу або виникла інша проблема.")
    finally:
        await state.clear()


# -----------------------------------------------------------
# View Chat Details and Add to Allowed
# -----------------------------------------------------------

@router.callback_query(ChatListCallback.filter(F.action == "view_chat_details"))
async def view_chat_details(callback_query: CallbackQuery, callback_data: ChatListCallback, state: FSMContext, telethon_manager: TelethonClientManager):
    chat_id = callback_data.chat_id
    current_page = callback_data.page if callback_data.page is not None else 0 # Отримуємо сторінку, якщо є

    logger.info(f"Користувач {callback_query.from_user.id} натиснув 'Переглянути' для чату ID: {chat_id}.")

    active_clients = telethon_manager.get_all_active_clients()
    if not active_clients:
        await callback_query.answer("Наразі немає активних Telethon клієнтів для перегляду деталей.", show_alert=True)
        return
    telethon_client = next(iter(active_clients.values()))

    if not telethon_client or not telethon_client.is_connected() or not await telethon_client.is_user_authorized():
        await callback_query.answer("Активний Telethon клієнт не підключений або не авторизований.", show_alert=True)
        return

    try:
        entity = await telethon_client.get_entity(chat_id)
        chat_title = entity.title
        participants_count = "N/A"
        if hasattr(entity, 'participants_count'):
            participants_count = entity.participants_count
        elif hasattr(entity, 'users_count'): # For channels
            participants_count = entity.users_count

        chat_type = "Group" if hasattr(entity, 'megagroup') and entity.megagroup else "Channel" if hasattr(entity, 'channel') else "Unknown"
        chat_username = getattr(entity, 'username', None)

        db_pool = await get_db_pool()
        existing_allowed_chats = await get_all_telethon_allowed_chats(db_pool)
        is_already_added = any(chat['chat_id'] == chat_id for chat in existing_allowed_chats)
        
        # Використовуємо ChatInfoCallback для кнопок на сторінці деталей
        builder = InlineKeyboardBuilder()

        if not is_already_added:
            builder.row(InlineKeyboardButton(text="Додати до дозволених", 
                                             callback_data=ChatInfoCallback(
                                                 action="add_allowed_chat_from_details", # Змінено дію для уникнення конфлікту
                                                 chat_id=chat_id,
                                                 page=current_page # Передаємо поточну сторінку назад
                                             ).pack()))
        else: # Якщо чат вже додано, пропонуємо видалити
            builder.row(InlineKeyboardButton(text="🗑️ Видалити чат",
                                             callback_data=ChatInfoCallback(
                                                 action="delete_allowed_chat",
                                                 chat_id=chat_id,
                                                 page=current_page
                                             ).pack()))
       
        # Кнопка повернення до списку (збереження пагінації)
        builder.row(InlineKeyboardButton(
            text="🔙 Повернутися до списку",
            callback_data=ChatListCallback(action="paginate_allowed_chats", page=current_page).pack()
        ))

        await callback_query.message.edit_text(
            f"**Деталі чату:**\n"
            f"**Назва:** {chat_title}\n"
            f"**ID:** `{chat_id}`\n"
            f"**Тип:** {chat_type}\n"
            f"**Юзернейм:** {chat_username if chat_username else 'Відсутній'}\n"
            f"**Учасників:** {participants_count}\n"
            f"**Статус:** {'✅ Вже додано до дозволених' if is_already_added else '❌ Ще не додано'}",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Помилка отримання деталей чату {chat_id}: {e}", exc_info=True)
        await callback_query.answer("Не вдалося отримати деталі чату. Перевірте лог.", show_alert=True)
        # Повертаємо до меню чат-матриці
        await callback_query.message.edit_text(
            "Виникла помилка при перегляді деталей чату.",
            reply_markup=get_chat_matrix_keyboard()
        )
    finally:
        await callback_query.answer()


@router.callback_query(ChatInfoCallback.filter(F.action == "add_allowed_chat_from_details")) # Змінено дію
async def add_chat_from_details(callback_query: CallbackQuery, callback_data: ChatInfoCallback, state: FSMContext, telethon_manager: TelethonClientManager):
    chat_id = callback_data.chat_id
    page = callback_data.page # Зберігаємо сторінку для повернення

    added_by_user_id = callback_query.from_user.id

    logger.info(f"Користувач {added_by_user_id} натиснув 'Додати до дозволених' для чату ID: {chat_id} (з деталей).")

    active_clients = telethon_manager.get_all_active_clients()
    if not active_clients:
        await callback_query.answer("Немає активних Telethon клієнтів для додавання чату.", show_alert=True)
        return
    
    telethon_client = next(iter(active_clients.values()))

    if not telethon_client or not telethon_client.is_connected() or not await telethon_client.is_user_authorized():
        await callback_query.answer("Активний Telethon клієнт не підключений або не авторизований. Додавання чату неможливе.", show_alert=True)
        return

    db_pool = await get_db_pool()

    try:
        entity = await telethon_client.get_entity(chat_id)
        chat_title = entity.title
        chat_type = "Group" if hasattr(entity, 'megagroup') and entity.megagroup else "Channel" if hasattr(entity, 'channel') else "Unknown"
        chat_username = getattr(entity, 'username', None)

        success = await add_telethon_allowed_chat(db_pool, chat_id, chat_title, chat_type, chat_username, added_by_user_id)
        
        if success:
            await callback_query.answer("Чат успішно додано до дозволених!", show_alert=True)
            # Після додавання, повертаємось до списку дозволених чатів
            # Змінено: Тепер передаємо telethon_manager та callback_data для пагінації
            await view_allowed_chats(callback_query, telethon_manager, ChatListCallback(action="paginate_allowed_chats", page=page))
        else:
            await callback_query.answer("Чат вже був доданий або виникла помилка.", show_alert=True)
            # Залишаємось на сторінці деталей або повертаємось до списку
            # Змінено: Тепер передаємо telethon_manager та callback_data для пагінації
            await view_chat_details(callback_query, ChatListCallback(action="view_chat_details", chat_id=chat_id, page=page), state, telethon_manager)


    except Exception as e:
        logger.error(f"Помилка додавання чату {chat_id} до дозволених з деталей: {e}", exc_info=True)
        await callback_query.answer(f"Помилка додавання чату. Перевірте лог.", show_alert=True)
    finally:
        await callback_query.answer()


# -----------------------------------------------------------
# View Allowed Chats
# -----------------------------------------------------------

@router.callback_query(AdminCallback.filter(F.action == "view_allowed_chats"))
@router.callback_query(ChatListCallback.filter(F.action == "paginate_allowed_chats")) # Додаємо пагінацію
async def view_allowed_chats(callback_query: CallbackQuery, telethon_manager: TelethonClientManager, callback_data: Optional[ChatListCallback] = None):
    logger.info(f"Користувач {callback_query.from_user.id} натиснув 'Переглянути дозволені чати' або переключив сторінку.")
    db_pool = await get_db_pool()
    
    current_page = callback_data.page if callback_data and callback_data.page is not None else 0
    chats_per_page = 5 # Визначте, скільки чатів на сторінку
    
    active_clients = telethon_manager.get_all_active_clients()

    if not active_clients:
        await callback_query.answer("Наразі немає активних Telethon клієнтів. Неможливо перевірити статус чатів.", show_alert=True)
        await callback_query.message.edit_text("Список дозволених чатів порожній або недоступний через відсутність активних клієнтів.", reply_markup=get_chat_matrix_keyboard())
        return

    telethon_client = next(iter(active_clients.values()))

    if not telethon_client or not telethon_client.is_connected() or not await telethon_client.is_user_authorized():
        await callback_query.answer("Активний Telethon клієнт не підключений або не авторизований. Перевірка статусу неможлива.", show_alert=True)
        await callback_query.message.edit_text("Список дозволених чатів порожній або недоступний.", reply_markup=get_chat_matrix_keyboard())
        return

    try:
        allowed_chats = await get_all_telethon_allowed_chats(db_pool)
        if not allowed_chats:
            await callback_query.message.edit_text("Наразі немає доданих дозволених чатів.", reply_markup=get_chat_matrix_keyboard())
            await callback_query.answer()
            return

        # ЗМІНА: Текст повідомлення тепер буде дуже коротким
        response_text = "**📜 Список підключених чатів:**\n\nОберіть чат зі списку нижче, щоб переглянути деталі або видалити його."
        
        # Передаємо повний список чатів та інформацію про пагінацію до функції клавіатури
        # Клавіатура сама сформує кнопки для поточної сторінки
        reply_markup = get_allowed_chats_list_keyboard(allowed_chats, current_page, chats_per_page)

        await callback_query.message.edit_text(
            response_text,
            reply_markup=reply_markup, # Використовуємо згенеровану клавіатуру
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Помилка перегляду дозволених чатів: {e}", exc_info=True)
        await callback_query.message.edit_text(f"Виникла помилка: {e}", reply_markup=get_chat_matrix_keyboard())
    finally:
        await callback_query.answer()


# -----------------------------------------------------------
# Back button handler
# -----------------------------------------------------------

@router.callback_query(AdminCallback.filter(F.action == "back_to_admin_main_menu_from_chat_matrix"))
async def back_to_admin_main_menu_from_chat_matrix(callback_query: CallbackQuery):
    logger.info(f"Користувач {callback_query.from_user.id} натиснув '⬅️ Назад' з Чат-матриці.")
    await callback_query.message.edit_text(
        "Панель адміністратора:",
        reply_markup=get_admin_main_keyboard()
    )
    await callback_query.answer()

# -----------------------------------------------------------
# Handlers for ChatInfoCallback (delete, back to list, etc.)
# -----------------------------------------------------------

@router.callback_query(ChatInfoCallback.filter(F.action == "delete_allowed_chat"))
async def ask_confirm_delete_chat(callback_query: CallbackQuery, callback_data: ChatInfoCallback):
    chat_id = callback_data.chat_id
    page = callback_data.page
    logger.info(f"Користувач {callback_query.from_user.id} натиснув 'Видалити чат' для ID: {chat_id}.")
    
    db_pool = await get_db_pool()
    chat_info = await get_telethon_allowed_chat_by_id(db_pool, chat_id)
    chat_title = chat_info['chat_title'] if chat_info else f"Чат з ID: {chat_id}"

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="✅ Підтвердити видалення",
        callback_data=ChatInfoCallback(action="confirm_delete_allowed_chat", chat_id=chat_id, page=page).pack()
    ))
    builder.row(InlineKeyboardButton(
        text="❌ Скасувати",
        callback_data=ChatInfoCallback(action="back_to_chat_info", chat_id=chat_id, page=page).pack()
    ))

    await callback_query.message.edit_text(
        f"**Ви впевнені, що хочете видалити чат '{chat_title}' (ID: `{chat_id}`)?**\n"
        "Ця дія є незворотною.",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback_query.answer()


@router.callback_query(ChatInfoCallback.filter(F.action == "confirm_delete_allowed_chat"))
async def confirm_delete_chat(callback_query: CallbackQuery, callback_data: ChatInfoCallback, telethon_manager: TelethonClientManager):
    chat_id = callback_data.chat_id
    page = callback_data.page
    logger.info(f"Користувач {callback_query.from_user.id} підтвердив видалення чату ID: {chat_id}.")
    
    db_pool = await get_db_pool()
    try:
        success = await delete_telethon_allowed_chat(db_pool, chat_id)
        if success:
            await callback_query.answer("Чат успішно видалено!", show_alert=True)
            # Повертаємось до списку дозволених чатів на тій же сторінці
            await view_allowed_chats(callback_query, telethon_manager, ChatListCallback(action="paginate_allowed_chats", page=page))
        else:
            await callback_query.answer("Не вдалося видалити чат. Можливо, його вже немає.", show_alert=True)
            # Повертаємось до списку дозволених чатів
            await view_allowed_chats(callback_query, telethon_manager, ChatListCallback(action="paginate_allowed_chats", page=page))
    except Exception as e:
        logger.error(f"Помилка видалення чату {chat_id}: {e}", exc_info=True)
        await callback_query.answer(f"Помилка при видаленні чату: {e}", show_alert=True)
        await view_allowed_chats(callback_query, telethon_manager, ChatListCallback(action="paginate_allowed_chats", page=page))
    finally:
        await callback_query.answer()


@router.callback_query(ChatInfoCallback.filter(F.action == "back_to_chat_info"))
async def back_to_chat_info_from_confirm(callback_query: CallbackQuery, callback_data: ChatInfoCallback, state: FSMContext, telethon_manager: TelethonClientManager):
    chat_id = callback_data.chat_id
    page = callback_data.page
    logger.info(f"Користувач {callback_query.from_user.id} повернувся до інформації про чат ID: {chat_id}.")
    # Викликаємо хендлер для відображення деталей чату
    await view_chat_details(callback_query, ChatListCallback(action="view_chat_details", chat_id=chat_id, page=page), state, telethon_manager)
    await callback_query.answer()


@router.callback_query(ChatListCallback.filter(F.action == "back_to_allowed_list"))
async def back_to_allowed_list_from_details(callback_query: CallbackQuery, callback_data: ChatListCallback, telethon_manager: TelethonClientManager):
    page = callback_data.page
    logger.info(f"Користувач {callback_query.from_user.id} повернувся до списку дозволених чатів зі сторінки деталей.")
    # Викликаємо хендлер для відображення списку дозволених чатів
    await view_allowed_chats(callback_query, telethon_manager, ChatListCallback(action="paginate_allowed_chats", page=page))
    await callback_query.answer()


# -----------------------------------------------------------
# Back to Chat Matrix Menu from anywhere inside Chat Matrix
# -----------------------------------------------------------

@router.callback_query(AdminCallback.filter(F.action == "chat_matrix_menu"))
async def return_to_chat_matrix_menu(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f"Користувач {callback_query.from_user.id} повернувся до головного меню Чат-матриці.")
    await state.clear()
    await callback_query.message.edit_text(
        "**⚙️ Меню Чат-матриці:**\nОберіть дію:",
        reply_markup=get_chat_matrix_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()