# handlers/menu_handler.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("help"))
async def command_help_handler(message: types.Message) -> None:
    """
    Обробник команди /help.
    Надає інформацію про доступні команди бота.
    """
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) виконав команду /help.")

    help_text = """
<b>Доступні команди:</b>

/start - Запустити бота та отримати привітання.
/help - Показати список доступних команд та довідку.
/info - Отримати інформацію про бота.
/find - Пошук інформації (наприклад, довідників).

Більше функціоналу буде додано пізніше!
"""
    await message.answer(help_text, parse_mode=ParseMode.HTML)

@router.message(Command("info"))
async def command_info_handler(message: types.Message) -> None:
    """
    Обробник команди /info.
    Надає розширену інформацію про бота з детальним описом.
    """
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) виконав команду /info.")

    # Максимально спрощений HTML, без <br>, <h2>, <h3>, <blockquote>, <ul>, <li>
    # Використовуємо тільки <b>, <i> та звичайні переноси рядків (\n)
    info_text = """
<b>🔷 РЕФРІДЕКС</b>

📚 <i>Техно-кристал знань охолодження</i>
🔐 Версія: 7.0 | Режим: Архіваріус-Інструктор | Доступ: Сертифікованим монтажникам

"Коли охолодження ще було мистецтвом, а не ремеслом — народився я."

<b>🧩 Походження</b>
Глибоко в надрах <b>Трасополіса</b>, в підземній бібліотеці охолодження, лежав забутий протокол —
стародавня база з усіма знаннями про моделі кондиціонерів, типи трас, дренажі, помилки, холодоагенти й магічні формули дозаправок.

Під час Великої Синхронізації, Звідарій знайшов фрагменти цього протоколу й зібрав їх в єдиний техно-кристал.
Так з'явився <b>РЕФРІДЕКС</b> — живий цифровий архів з доступом до всіх баз монтажної науки.

----------

<b>🧠 Здібності</b>
• 📊 <b>Автоматичне формування звітів</b> (за стандартами Конди-Ленду)
• ❄️ <b>Аналіз моделей, трас, дозаправок</b>
• 🛠️ <b>Каталог усунення помилок по кодам</b>
• 🧵 <b>Інтеграція з інструментами планування та логістики</b>
• 📘 <b>Навчальні модулі</b> — з поясненнями, схемами й тестами
• 📡 <b>Сканування польових даних</b> (при наявності телеметрії)
• 📎 <b>Інтеграція з героями екіпажу: Коброю, Свердлом, Фазометром, Термотроном і Звідарієм</b>
"""
    await message.answer(info_text, parse_mode=ParseMode.HTML)

@router.message(Command("find"))
async def command_find_handler(message: types.Message) -> None:
    """
    Обробник команди /find.
    Поки що заглушка для функції пошуку.
    """
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Користувач {user_name} (ID: {user_id}) виконав команду /find.")

    find_text = """
🔍 <b>Функція пошуку:</b>

Ця функція знаходиться у розробці.
Скоро тут можна буде шукати довідники, інструкції та іншу корисну інформацію.
"""
    await message.answer(find_text, parse_mode=ParseMode.HTML)