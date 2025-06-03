# keyboards/__init__.py

# Експортуємо функції з admin_keyboard.py
from .admin_keyboard import (
    get_admin_main_keyboard,
    get_users_list_keyboard,
    get_pagination_keyboard,
    get_user_actions_keyboard,
    get_confirm_action_keyboard,
    get_access_level_keyboard,
    get_telethon_actions_keyboard
)

# Оскільки keyboards/inline_keyboard.py порожній, ми не імпортуємо з нього нічого.
# from .inline_keyboard import ... (закоментовано або видалено)

# Експортуємо функції та змінні з reply_keyboard.py
# Зверніть увагу: get_remove_keyboard більше не імпортується, оскільки її немає у файлі.
from .reply_keyboard import (
    get_main_menu_keyboard,
    BUTTONS_PER_PAGE,
    BUTTONS_CONFIG
)