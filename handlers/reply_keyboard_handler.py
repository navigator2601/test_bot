# handlers/reply_keyboard_handler.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.reply_keyboard import create_main_menu_keyboard, create_additional_functions_keyboard
from keyboards.inline_keyboard import create_brands_keyboard, create_types_keyboard, create_models_keyboard
import random
from database.connection import Database
from database import queries
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot_test.telethon_client import get_chat_messages as telethon_get_chat_messages
import re
from datetime import datetime, timedelta
from decimal import Decimal

# ... (інший код файлу) ...

# Ініціалізація маршрутизатора
router = Router()

def decimal_to_dms(decimal_degrees):
    """Перетворює десяткові градуси в формат ДМС (градуси, хвилини, секунди)."""
    degrees = int(decimal_degrees)
    minutes_decimal = abs(decimal_degrees - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    return f"{degrees}°{minutes}'{seconds:.2f}\""

async def read_and_filter_chat(telegram_chat_id: int, chat_id: int, start_date: datetime, end_date: datetime):
    """Читає повідомлення з чату Telethon за вказаний період, фільтрує та обробляє їх."""
    messages = await telethon_get_chat_messages(chat_id, limit=None, min_date=start_date, max_date=end_date)
    found_data = []
    pattern = re.compile(
        r"^(\d+)\s+м\.\s+([^\s]+)\s+вул\.\s+([^\s]+)\s+(?:(?P<region>\([^)]*\)\s+))?([^\s]+)\s+"
        r"(-?\d+\.\d+)\s+-\s+(-?\d+\.\d+)\s+"
        r"(?:(?P<start_date>\d{2}\.\d{2}\.\d{4})\s*(?:(?P<end_date>\d{2}\.\d{2}\.\d{4}))?\s*)?"
        r"(?P<cond_info>[\d\\]+к\s+і\s+[\d\\]+н(?:,\s*[\d\\]+к\s+і\s+[\d\\]+н)*)?(?P<notes>\s+.*)?$"
    )

    if messages:
        for message in messages:
            if message.date >= start_date and message.date <= end_date and message.text:
                match = pattern.match(message.text)
                if match:
                    shop_number = match.group(1)
                    city = match.group(2)
                    address = match.group(3)
                    latitude = Decimal(match.group(6))
                    longitude = Decimal(match.group(7))
                    start = match.group("start_date")
                    end = match.group("end_date")
                    dates = ""
                    if start:
                        dates += f"{start}"
                        if end:
                            dates += f" - {end}"
                    cond_info = match.group("cond_info")
                    notes = match.group("notes") if match.group("notes") else ""

                    found_data.append(
                        f"Номер магазину: {shop_number}\n"
                        f"Населений пункт, адреса: {city}, вул. {address}\n"
                        f"Дата початку і закінчення робіт: {dates if dates else 'Немає даних'}\n"
                        f"Кількість і потужність кондиціонерів: {cond_info if cond_info else 'Немає даних'}{notes}\n"
                        f"Координати (ДМС): {decimal_to_dms(latitude)} широти, {decimal_to_dms(longitude)} довготи\n"
                    )

    if found_data:
        response = "Знайдено наступні об'єкти:\n\n" + "\n\n".join(found_data)
        await bot.send_message(telegram_chat_id, response)
    else:
        await bot.send_message(telegram_chat_id, "За останні 7 днів об'єктів у заданому форматі не знайдено.")

# Список повідомлень для допомоги
HELP_MESSAGES = [
    """
    👋 Привіт! Я бот-помічник з кондиціонерів.

    Мій основний функціонал:

    📚 **Каталог:** Перегляд доступних моделей кондиціонерів з їх характеристиками.
    📖 **Довідник:** Корисні матеріали, інструкції та відповіді на часті запитання про кондиціонери.
    🕵️ **Пошук:** Інтелектуальний пошук інформації за вашими запитами.
    ⚠️ **Коди помилок:** Пошук розшифровки кодів помилок для діагностики проблем.
    🛠️ **Технічна інформація:** Загальні відомості про монтаж кондиціонерів.
    ➡️ **Додаткові функції:** Різноманітні калькулятори та корисні інструменти.

    Використовуйте кнопки в меню для навігації. Якщо у вас виникнуть питання, звертайтеся!
    """,
    """
    👋 Ласкаво просимо до бота-помічника з кондиціонерів!

    Я тут, щоб допомогти вам з вибором, розумінням та обслуговуванням кондиціонерів.

    Основні розділи:

    * **📚 Каталог:** Переглядайте наш асортимент кондиціонерів з детальними характеристиками. Просто натисніть кнопку "📚 Каталог".
    * **📖 Довідник:** Тут ви знайдете навчальні матеріали, поради та відповіді на поширені запитання (FAQ) про різні аспекти кондиціонування.
    * **🕵️ Пошук:** Спробуйте мій інтелектуальний пошук, щоб знайти інформацію за ключовими словами або фразами. Наприклад, запитайте: "як розрахувати потужність кондиціонера?".
    * **🆘 Допомога:** Цей розділ містить опис моїх основних функцій та список доступних команд (якщо ви використовуєте текстові команди, наприклад, `/start`, `/info` тощо).
    * **⚠️ Коди помилок:** Якщо ваш кондиціонер показує код помилки, ви можете знайти його розшифровку тут. Натисніть кнопку "⚠️ Коди помилок" та введіть код.
    * **🛠️ Технічна інформація:** Отримайте загальні відомості та рекомендації щодо встановлення кондиціонерів.
    * **➡️ Додаткові функції:** Перейдіть до іншої клавіатури, де ви знайдете корисні калькулятори та інші інструменти, пов'язані з кондиціонуванням.

    Для навігації використовуйте кнопки в головному меню. Якщо вам потрібна додаткова допомога, звертайтеся!
    """,
    """
    👋 Вітаю! Я ваш персональний помічник у світі кондиціонерів.

    Я можу допомогти вам:

    * **З легкістю знайти потрібний кондиціонер** у нашому каталозі.
    * **Розширити свої знання** про кондиціонування за допомогою довідкових матеріалів.
    * **Швидко знайти інформацію** завдяки інтелектуальному пошуку.
    * **Зрозуміти коди помилок** вашого обладнання.
    * **Ознайомитися з основами монтажу.**
    * **Використовувати корисні інструменти та калькулятори.**

    Просто натисніть відповідну кнопку в головному меню, щоб скористатися моїми функціями.
    """
]

# Обробник для основного меню, включаючи "📚 Каталог"
@router.message(F.text.in_({
    "📚 Каталог",
    "📖 Довідник",
    "🕵️ Пошук",
    "🆘 Допомога",
    "⚠️ Коди помилок",
    "🛠️ Технічна інформація",
    "📐️ Додаткові функції"
}))
async def handle_main_menu(message: Message):
    print(f"Обробляється команда головного меню: {message.text}")
    if message.text == "📚 Каталог":
        keyboard = await create_brands_keyboard()
        await message.answer("Ви обрали каталог, будь ласка, оберіть бренд внизу:", reply_markup=keyboard)
    elif message.text == "📖 Довідник":
        await message.answer("Ви обрали: Довідник. Тут зібрані корисні матеріали.", reply_markup=create_main_menu_keyboard())
    elif message.text == "🕵️ Пошук":
        await message.answer("Ви обрали: Пошук. Введіть, що саме ви хочете знайти.", reply_markup=create_main_menu_keyboard())
    elif message.text == "🆘 Допомога":
        await message.answer(random.choice(HELP_MESSAGES), reply_markup=create_main_menu_keyboard())
    elif message.text == "⚠️ Коди помилок":
        await message.answer("Ви обрали: Коди помилок. Введіть код помилки для отримання інформації.", reply_markup=create_main_menu_keyboard())
    elif message.text == "🛠️ Технічна інформація":
        await message.answer("Ви обрали: Технічна інформація. Тут ви знайдете інформацію про монтаж.", reply_markup=create_main_menu_keyboard())
    elif message.text == "📐️ Додаткові функції":
        await message.answer("Ви обрали: Додаткові функції. Оберіть одну з доступних опцій.", reply_markup=create_additional_functions_keyboard())

# Обробник для команди /help
@router.message(F.text == "/help")
async def handle_help_command(message: Message):
    print(f"Обробляється команда: /help")
    await message.answer(random.choice(HELP_MESSAGES), reply_markup=create_main_menu_keyboard())

# Обробник для команди /info
@router.message(F.text == "/info")
async def handle_info_command(message: Message):
    """
    Відповідає на команду /info, надаючи користувачеві інформацію про функціонал бота.
    """
    print(f"Обробляється команда: /info")
    info_message = f"""
    👋 Привіт, {message.from_user.first_name}! Я бот-помічник з кондиціонерів.

    Мій основний функціонал допомагає вам:

    * З легкістю знаходити потрібні моделі кондиціонерів у нашому каталозі з детальними характеристиками.
    * Розширювати свої знання про кондиціонування за допомогою корисних довідкових матеріалів та відповідей на часті запитання.
    * Швидко знаходити необхідну інформацію завдяки інтелектуальному пошуку за ключовими словами.
    * Діагностувати проблеми з вашим обладнанням, знаходячи розшифровки кодів помилок.
    * Ознайомлюватися з основами монтажу кондиціонерів.
    * Користуватися різноманітними інструментами та калькуляторами для розрахунків та інших корисних функцій.
    """
    await message.answer(info_message, reply_markup=create_main_menu_keyboard())

# Обробник для додаткових функцій
@router.message(F.text.in_({
    "🧮 Калькулятор потужності",
    "📊 Графіки енерговитрат",
    "🔙 Назад до головного меню"
}))
async def handle_additional_functions_menu(message: Message):
    print(f"Обробляється команда додаткових функцій: {message.text}")
    if message.text == "🧮 Калькулятор потужності":
        await message.answer("Ви обрали: Калькулятор потужності. Розрахуйте необхідну потужність кондиціонера.")
    elif message.text == "📊 Графіки енерговитрат":
        await message.answer("Ви обрали: Графіки енергоспоживання.")
    elif message.text == "🔙 Назад до головного меню":
        await message.answer("Повернення до головного меню.", reply_markup=create_main_menu_keyboard())

# Обробники callback-запитів для каталогу
@router.callback_query(F.data.startswith("brand_"))
async def handle_brand_selection(callback_query: CallbackQuery):
    """Обробляє вибір бренду."""
    print(f"Обробляється callback: {callback_query.data}")
    brand_id = int(callback_query.data.split("_")[1])
    print(f"Обрано brand_id: {brand_id}")
    db = Database()
    await db.connect()
    brand_info = await db.fetchrow(queries.GET_BRAND_BY_ID, brand_id)
    print(f"Інформація про бренд: {brand_info}")
    await db.disconnect()
    brand_name = brand_info['name'] if brand_info else "Невідомий бренд"
    print(f"Назва бренду: {brand_name}")

    keyboard = await create_types_keyboard(brand_id)
    print(f"Створено клавіатуру типів: {keyboard}")
    await callback_query.message.edit_text(f"Добре! Оберіть тип кондиціонера для бренду '{brand_name}':", reply_markup=keyboard)
    await callback_query.answer()
    print("Відправлено відповідь.")

@router.callback_query(F.data.startswith("type_"))
async def handle_type_selection(callback_query: CallbackQuery):
    """Обробляє вибір типу кондиціонера."""
    print(f"Обробляється callback: {callback_query.data}")
    _, brand_id, type_id = callback_query.data.split("_")
    brand_id = int(brand_id)
    type_id = int(type_id)
    print(f"Обрано brand_id: {brand_id}, type_id: {type_id}")
    db = Database()
    await db.connect()
    type_info = await db.fetchrow(queries.GET_TYPE_BY_ID, type_id)
    brand_info = await db.fetchrow(queries.GET_BRAND_BY_ID, brand_id)
    print(f"Інформація про тип: {type_info}, інформація про бренд: {brand_info}")
    await db.disconnect()
    type_name = type_info['name'] if type_info else "Невідомий тип"
    brand_name = brand_info['name'] if brand_info and 'name' in brand_info else "Невідомий бренд"
    print(f"Назва типу: {type_name}, назва бренду: {brand_name}")

    keyboard = await create_models_keyboard(brand_id, type_id)
    print(f"Створено клавіатуру моделей: {keyboard}")
    await callback_query.message.edit_text(f"Чудово! Оберіть модель кондиціонера для типу '{type_name}' бренду '{brand_name}':", reply_markup=keyboard)
    await callback_query.answer()
    print("Відправлено відповідь.")

# Обробники callback-запитів для каталогу (handle_brand_selection, handle_type_selection залишаються без змін)

@router.callback_query(F.data.startswith("model_"))
async def handle_model_selection(callback_query: CallbackQuery):
    """Обробляє вибір моделі кондиціонера та пропонує обрати інформацію."""
    print(f"!!! ВИКЛИКАНО handle_model_selection З ДАНИМИ: {callback_query.data} !!!")
    _, brand_id, type_id, model_id = callback_query.data.split("_")
    print(f"Обрано brand_id: {brand_id}, type_id: {type_id}, model_id: {model_id}")
    db = Database()
    await db.connect()
    brand_info = await db.fetchrow(queries.GET_BRAND_BY_ID, int(brand_id))
    type_info = await db.fetchrow(queries.GET_TYPE_BY_ID, int(type_id))
    model_info = await db.fetchrow(
        queries.GET_MODEL_BY_ID,
        int(model_id)
    )
    await db.disconnect()

    brand_name = brand_info['name'] if brand_info else "Невідомий бренд"
    type_name = type_info['name'] if type_info else "Невідомий тип"
    model_full_name = f"{model_info['btu_value'] // 1000:02d}{model_info['type_abbreviation']} ({model_info['brand_name']})" if model_info else "Невідома модель"

    print(f"Назва бренду: {brand_name}, назва типу: {type_name}, повна назва моделі: {model_full_name}")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Розміри внутр. блоку", callback_data=f"model_info_{brand_id}_{type_id}_{model_id}_indoor")],
        [InlineKeyboardButton(text="📏 Розміри зовн. блоку", callback_data=f"model_info_{brand_id}_{type_id}_{model_id}_outdoor")],
        [InlineKeyboardButton(text="⚙️ Технічна інформація", callback_data=f"model_info_{brand_id}_{type_id}_{model_id}_technical")],
        [InlineKeyboardButton(text="ℹ️ Повна інформація", callback_data=f"model_info_{brand_id}_{type_id}_{model_id}_full")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_models_{brand_id}_{type_id}")],
    ])
    print(f"Створено клавіатуру інформації про модель: {keyboard}")

    await callback_query.message.edit_reply_markup(reply_markup=None) # Явно видаляємо попередню клавіатуру
    await callback_query.message.edit_text(f"Ви обрали модель: {model_full_name}. Яка саме інформація вас цікавить?", reply_markup=keyboard)
    await callback_query.answer()
    print("Відправлено відповідь.")

@router.callback_query(F.data.startswith("model_info_"))
async def handle_model_info(callback_query: CallbackQuery):
    """Обробляє натискання на кнопки інформації про модель."""
    print(f"Обробляється callback: {callback_query.data}")
    parts = callback_query.data.split("_")
    if len(parts) == 5: # Тепер очікуємо 5 частин: model_info_brand_id_type_id_model_id_info_type
        _, brand_id, type_id, model_id, info_type = parts
        model_id = int(model_id)

        db = Database()
        await db.connect()

        if info_type == "indoor":
            dimensions = await db.fetchrow(queries.GET_INDOOR_DIMENSIONS_BY_MODEL_ID, model_id)
            await db.disconnect()
            if dimensions:
                message = (
                    f"📏 Розміри внутрішнього блоку:\n"
                    f"Довжина - {dimensions['lenght_mm']} мм\n"
                    f"Глибина - {dimensions['depth_mm']} мм\n"
                    f"Висота - {dimensions['height_mm']} мм"
                )
                await callback_query.message.answer(message)
            else:
                await callback_query.message.answer("📏 Розміри внутрішнього блоку для цієї моделі не знайдено.")
        elif info_type == "outdoor":
            await callback_query.message.answer("📏 Розміри зовнішнього блоку: Функція в розробці")
        elif info_type == "technical":
            await callback_query.message.answer("⚙️ Технічна інформація: Функція в розробці")
        elif info_type == "full":
            await callback_query.message.answer("ℹ️ Повна інформація: Функція в розробці")
        else:
            await db.disconnect()

    await callback_query.answer()

@router.callback_query(F.data.startswith("back_to_models_"))
async def handle_back_to_models(callback_query: CallbackQuery):
    """Повертає до списку моделей."""
    print(f"Обробляється callback: {callback_query.data}")
    _, brand_id, type_id = callback_query.data.split("_")
    brand_id = int(brand_id)
    type_id = int(type_id)

    keyboard = await create_models_keyboard(brand_id, type_id)
    await callback_query.message.edit_text("Оберіть модель:", reply_markup=keyboard)
    await callback_query.answer()