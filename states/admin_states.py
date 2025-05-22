# states/admin_states.py
from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    admin_panel = State() # Стан для адмін-панелі
    viewing_users = State() # Перегляд списку користувачів
    managing_user_access = State() # Управління конкретним користувачем
    waiting_for_access_level = State() # Очікування нового рівня доступу
    waiting_for_user_id_to_add = State() # Очікування User ID для ручного додавання

    # НОВІ СТАНИ ДЛЯ АВТОРИЗАЦІЇ TELETHON
    waiting_for_telethon_code = State() # Очікування коду авторизації від Telegram
    waiting_for_telethon_password = State() # Очікування паролю двохетапної перевірки