# keyboards/__init__.py

# Експортуємо функції з admin_keyboard.py
from .admin_keyboard import (
    get_admin_main_keyboard,
    get_users_list_keyboard,
    # get_pagination_keyboard, # Якщо її видалили, то і тут прибираємо
    get_user_actions_keyboard,
    get_confirm_action_keyboard,
    get_access_level_keyboard,
    get_telethon_actions_keyboard
)

# Оскільки keyboards/inline_keyboard.py порожній, ми не імпортуємо з нього нічого.
# from .inline_keyboard import ... (закоментовано або видалено)

# Експортуємо функції та змінні з reply_keyboard.py
from .reply_keyboard import (
    get_main_menu_keyboard,
    get_main_menu_pages_info # <--- ДОДАНО: нова функція для отримання інфо про сторінки
)

# З common.constants ми імпортуємо BUTTONS_PER_PAGE, ALL_MENU_BUTTONS.
# Тому не потрібно їх імпортувати з reply_keyboard.py