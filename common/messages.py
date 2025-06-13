# common/messages.py
import random
# from common.constants import ACCESS_LEVEL_BUTTONS # Переконайтеся, що у вас є цей імпорт в common.constants, якщо використовується

# Існуючі повідомлення адміністратора
ADMIN_WELCOME_MESSAGES = [
    "<b>⚙️ Refridex OS:</b>\n “Сигнал підтверджено. Відкриваю панель командування ядром.”",
    "<b>💻 Refridex OS:</b>\n “Адмін-доступ авторизовано. Обери свій шлях, Контролере.”",
    "<b>🔐 Refridex OS:</b>\n “Ти пройшов крізь ідентифікацію. Панель адміністратора активна.”",
    "<b>🧊 Refridex OS:</b>\n “Привіт, Хранителю системи. Параметри під контролем.”",
    "<b>📡 Refridex OS:</b>\n “Підключення до внутрішнього інтерфейсу встановлено. Команди доступні.”",
    "<b>🪞 Refridex OS:</b>\n “Панель керування розблокована. Твоя воля — мій протокол.”",
    "<b>🧬 Refridex OS:</b>\n “Ти в центрі управління. Система слухає.”",
    "<b>🧠 Refridex OS:</b>\n “Адмін-інтерфейс запущено. Дії очікуються...”",
    "<b>💿 Refridex OS:</b>\n “Контрольна консоль активна. Вибери операцію, Модераторе.”",
    "<b>⚡ Refridex OS:</b>\n “Нульовий доступ обійдено. Панель відкрито через альтернативний порт.”",
    "<b>🧯 Refridex OS:</b>\n “Адміністратор з'явився. Відкриваю можливості управління.”",
    "<b>📟 Refridex OS:</b>\n “Доступ до панелі отримано. Зчитування привілеїв...”",
    "<b>🔧 Refridex OS:</b>\n “Серце системи відкрито. Виконуй свій протокол.”",
    "<b>🧭 Refridex OS:</b>\n “Ти — в командному центрі. Визнач свою ціль.”",
    "<b>🔊 Refridex OS:</b>\n “Я слухаю, Керівнику. Обирай наступну дію.”"
]

# --- НОВІ ПОВІДОМЛЕННЯ ДЛЯ TELETHON АВТОРИЗАЦІЇ ---
TELETHON_AUTH_MESSAGES = {
    "telethon_main_menu": "Оберіть дію для управління TeleKey (API-зв'язком):", # НОВЕ
    "start_auth_process_user_notif": "Починаємо авторизацію Telethon...",
    "already_authorized": "Telethon клієнт вже авторизований. Якщо хочете перевидати сесію, спочатку відключіться.",
    "session_loaded_success": "Telethon клієнт успішно авторизований за збереженою сесією!",
    "init_error": "Помилка ініціалізації Telethon: {error_message}. Спробуйте знову.",
    "request_phone_number": "Будь ласка, надішліть номер телефону для авторизації Telethon у форматі `+380XXXXXXXXX` (без пробілів):",
    "invalid_phone_format": "Будь ласка, введіть коректний номер телефону у форматі `+380XXXXXXXXX` (без пробілів):",
    "phone_too_long": "Номер телефону занадто довгий. Будь ласка, перевірте.", # НОВЕ
    "phone_too_short": "Номер телефону занадто короткий. Будь ласка, перевірте.", # НОВЕ
    "code_sent": "Код авторизації відправлено на номер `{phone_number}`. Будь ласка, введіть код:",
    "new_code_requested": "Надіслано новий код. Перевірте Telegram.", # НОВЕ
    "rpc_error_send_code_generic": "Виникла помилка під час надсилання коду. Можливо, номер неправильний або виникла проблема з Telegram API.",
    "phone_number_invalid": "Некоректний номер телефону. Будь ласка, перевірте і спробуйте знову.",
    "flood_wait": "Занадто багато спроб. Будь ласка, спробуйте через {seconds} секунд.",
    "phone_number_banned": "Номер телефону заблокований.",
    "general_error_send_code": "Сталася неочікувана помилка: {error_message}. Спробуйте знову.",
    "missing_state_data": "Сталася помилка даних. Спробуйте розпочати авторизацію знову.",
    "code_expired": "Термін дії коду минув. Будь ласка, почніть авторизацію знову.",
    "invalid_code": "Неправильний код. Будь ласка, спробуйте ще раз:",
    "auth_success": "✅ Telethon клієнт успішно авторизований!",
    "password_needed": "Вам потрібна двофакторна автентифікація. Будь ласка, введіть пароль від хмарного сховища:",
    "rpc_error_signin_generic": "Помилка при авторизації: {error_message}. Спробуйте знову.",
    "general_error_signin": "Сталася неочікувана помилка: {error_message}. Спробуйте знову.",
    "incorrect_password": "Неправильний пароль. Будь ласка, спробуйте ще раз.",
    "unknown_password_auth_error": "Невідома помилка при автентифікації з паролем. Спробуйте знову.",
    "auth_canceled": "Авторизація скасована.",
    "client_disconnected": "❌ Telethon клієнт відключено.",
    "client_not_authorized_disconnect": "Telethon клієнт не був авторизований.",
    "telethon_actions_menu_prompt": "Оберіть дію для управління TeleKey (API-зв'язком):", # Це може бути дублікат "telethon_main_menu", можете вирішити, який використовувати
    "telethon_checking_status": "Перевіряю статус Telethon...",
    "telethon_status_authorized": (
        "✅ **Telethon клієнт авторизований.**\n"
        "**ID:** `{id}`\n"
        "**Ім'я:** `{first_name}`\n"
        "**Юзернейм:** `@{username}`"
    ),
    "telethon_status_not_authorized": "❌ **Telethon клієнт не авторизований.**",
    "telethon_no_sessions_found": "Наразі немає збережених Telethon сесій. Будь ласка, авторизуйте клієнта.", # НОВЕ
    "telethon_no_sessions_to_delete": "Наразі немає збережених Telethon сесій для видалення.", # НОВЕ
    "telethon_session_select_delete": "Оберіть сесію для видалення:", # НОВЕ
    "session_deleted": "Сесія для `{phone_number}` успішно видалена.", # НОВЕ
}
# --- КІНЕЦЬ НОВИХ ПОВІДОМЛЕНЬ ---

# --- Admin Panel Messages (additional) ---
# Ці повідомлення є більш загальними для адмін-панелі, ніж специфічними для Telethon,
# тому їх краще тримати окремо або в іншій секції.
ADMIN_WELCOME_MESSAGE_DEFAULT = "Ласкаво просимо, Адміністраторе! Оберіть дію:"
ADMIN_RETURN_MAIN_PANEL = "Ви повернулись до головної адмін-панелі."
ADMIN_EXIT_MESSAGE = "Ви вийшли з адмін-панелі. Повернення до головного меню."
ADMIN_USER_MATRIX_PROMPT = "<b>👥 Юзер-матриця:</b>\nОберіть користувача для управління або перегляньте сторінки."
ADMIN_USER_NOT_FOUND = "Користувача не знайдено."
ADMIN_ERROR_NO_USER_ID = "Помилка: не знайдено ID користувача."
ADMIN_ERROR_NO_CONFIRM_DATA = "Помилка: не знайдено даних для підтвердження."
ADMIN_ERROR_UNKNOWN_STEP = "Невідомий крок авторизації. Будь ласка, спробуйте знову."
ADMIN_ACTION_CANCELED = "Дію скасовано."
ADMIN_TELETHON_MAIN_PROMPT = "<b>🔐 TeleKey · Авторизація API-зв’язку:</b>\n\nОберіть дію для управління Telethon API:"
ADMIN_TELETHON_ALREADY_CONNECTED = "Принаймні один клієнт Telethon вже підключено. Якщо потрібно переавторизувати, спочатку відключіть."
ADMIN_TELETHON_AUTH_START = "Початок авторизації Telethon..."
ADMIN_TELETHON_ENTER_PHONE = "Будь ласка, введіть номер телефону для авторизації Telethon (у форматі +380XXXXXXXXX):"
ADMIN_TELETHON_INVALID_PHONE = "Будь ласка, введіть коректний номер телефону у форматі +380XXXXXXXXX."
ADMIN_TELETHON_CODE_SENT = "Відправлено код підтвердження на номер {phone_number}. Будь ласка, введіть його:"
ADMIN_TELETHON_SEND_CODE_ERROR = "Не вдалося відправити код: {error}. Спробуйте ще раз або перевірте номер."
ADMIN_TELETHON_ENTER_CODE = "Будь ласка, введіть коректний цифровий код підтвердження."
ADMIN_TELETHON_NO_PHONE_IN_STATE = "Помилка: номер телефону не знайдено. Спробуйте почати авторизацію знову."
ADMIN_TELETHON_CHECKING_CODE = "Перевірка коду..."
ADMIN_TELETHON_AUTH_SUCCESS = "Авторизація Telethon успішно завершена."
ADMIN_TELETHON_AUTH_ERROR = "Помилка авторизації Telethon: {error}. Спробуйте ще раз."
ADMIN_TELETHON_CLIENT_NOT_CONNECTED = "Клієнт Telethon не підключено. Будь ласка, авторизуйтесь спочатку."
ADMIN_TELETHON_GET_INFO_PROMPT = "Отримання інформації про користувача Telethon..."
ADMIN_TELETHON_GET_INFO_ERROR = "Помилка при отриманні інформації про користувача Telethon: {error}"
ADMIN_TELETHON_JOIN_CHANNEL_PROMPT = "Будь ласка, надішліть посилання або username каналу/чату, до якого потрібно приєднатися:"
ADMIN_TELETHON_JOIN_CHANNEL_SUCCESS = "✅ Успішно приєднано до каналу/чату: <code>{channel_link_or_username}</code>"
ADMIN_TELETHON_JOIN_CHANNEL_ERROR = "❌ Не вдалося приєднатися до каналу/чату <code>{channel_link_or_username}</code>: {error}"
ADMIN_TELETHON_CHATS_LOADING = "Завантаження чатів. Це може зайняти деякий час..."
ADMIN_TELETHON_NO_CHATS_FOUND = "Не знайдено жодного чату або каналу."
ADMIN_TELETHON_CHATS_ERROR = "Помилка при завантаженні діалогів: {error}"
ADMIN_TELETHON_PARTIAL_CHATS_INFO = "Показано перші {count} з {total} чатів. Для повного списку використовуйте інший інструмент."
ADMIN_TELETHON_CHECK_STATUS_CONNECTED = "✅ Telethon клієнт ({phone_number}) підключено."
ADMIN_TELETHON_CHECK_STATUS_DISCONNECTED = "❌ Telethon клієнт не підключено або не знайдено активних клієнтів."
ADMIN_USER_ACCESS_LEVEL_PROMPT = "Оберіть новий рівень доступу для користувача <code>{user_id}</code>:"
ADMIN_USER_ACCESS_LEVEL_CHANGED = "Рівень доступу для користувача <code>{user_id}</code> успішно встановлено на <b>{access_level}</b>."
ADMIN_USER_MANAGEMENT_ACTION_CONFIRM = "Ви впевнені, що хочете <b>{action_text}</b> користувача <code>{user_id}</code>?"
ADMIN_USER_MANAGEMENT_ACTION_SUCCESS = "Користувача <code>{user_id}</code> успішно <b>{status_text}</b>."
ADMIN_ACTION_CANCELED_USER_MANAGEMENT = "Дію скасовано. Повернення до управління користувачем <code>{user_id}</code>."
ADMIN_GENERAL_ERROR_RETURN_TO_MAIN = "Сталася помилка. Повернення до головної адмін-панелі."
ADMIN_ACTION_CANCELED_ALERT = "Дію скасовано." # Додано для callback.answer
ADMIN_ACCESS_LEVEL_CHANGED_ALERT = "Рівень доступу змінено на {access_level}." # Додано для callback.answer
ADMIN_USER_ACTION_SUCCESS_ALERT = "Користувача {user_id} успішно {status_text}." # Додано для callback.answer


# Додаємо текст для команд /help, /info, /find
HELP_MESSAGE_TEXT = """
<b>Доступні команди:</b>

/start - Запустити бота та отримати привітання.
/help - Показати список доступних команд та довідку.
/info - Отримати інформацію про бота.
/find - Пошук інформації (наприклад, довідників).

Більше функціоналу буде додано пізніше!
"""

INFO_MESSAGE_TEXT = """
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

FIND_MESSAGE_TEXT = """
🔍 <b>Функція пошуку:</b>

Ця функція знаходиться у розробці.
Скоро тут можна буде шукати довідники, інструкції та іншу корисну інформацію.
"""

def get_access_level_description(access_level: int, access_buttons: list[tuple[int, str]]) -> tuple[str, str]:
    """
    Повертає назву та опис рівня доступу.

    :param access_level: Числовий рівень доступу користувача.
    :param access_buttons: Список кортежів (рівень, назва) для кнопок рівня доступу.
    :return: Кортеж (назва_рівня: str, опис_рівня: str).
    """
    if access_level == 0:
        return "🌐 Гість Системи", "Має мінімальний доступ до базових функцій."
    elif 1 <= access_level <= 2:
        return "🎮 Пілот Блоку", "Може управляти деякими режимами та викликати діагностику."
    elif 3 <= access_level <= 5:
        return "🔧 Інженер Зони", "Має доступ до звітності, розширених налаштувань."
    elif 6 <= access_level <= 9:
        return "🧠 Техно-Оператор HVAC", "Знає, що таке субохолодження. Аналізує дані та зберігає баланс."
    elif access_level >= 10:
        return "🧬 Адміністратор Ядра", "Має ключ до всіх баз. Може перепрошити саму суть Рефрідекса."
    else:
        return "❓ Невідомий рівень доступу", "Зверніться до адміністратора."

def get_random_admin_welcome_message() -> str:
    """
    Повертає випадкове привітальне повідомлення для адмін-панелі.
    """
    return random.choice(ADMIN_WELCOME_MESSAGES)

def get_user_details_text(user_info: dict, is_authorized: bool, access_buttons: list[tuple[int, str]]) -> str:
    """
    Формує текстове повідомлення з детальною інформацією про користувача.

    :param user_info: Словник з інформацією про користувача (id, first_name, last_name, username, access_level).
    :param is_authorized: Булеве значення, що вказує, чи авторизований користувач.
    :param access_buttons: Список кортежів (рівень, назва) для визначення назв рівнів доступу.
    :return: Форматований рядок з інформацією про користувача.
    """
    user_id = user_info.get('id')
    current_level = user_info.get('access_level', 0)

    # Використовуємо існуючу функцію з цього ж файлу
    access_level_name, _ = get_access_level_description(current_level, access_buttons)

    user_info_text = (
        f"<b>🛠️ Інформація про користувача:</b>\n\n"
        f"<b>ID:</b> <code>{user_info.get('id')}</code>\n"
        f"<b>Ім'я:</b> {user_info.get('first_name', 'N/A')} {user_info.get('last_name', '')}\n"
        f"<b>Username:</b> @{user_info.get('username', 'N/A')}\n"
        f"<b>Рівень доступу:</b> {access_level_name} ({current_level})\n"
        f"<b>Статус:</b> {'Авторизований ✅' if is_authorized else 'Неавторизований ❌'}"
    )
    return user_info_text