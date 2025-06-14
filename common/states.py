# common/states.py
from aiogram.fsm.state import State, StatesGroup

class MenuStates(StatesGroup):
    """FSM-стани для головного меню."""
    main_menu = State()
    any = State() # Залишаємо, припускаючи, що ви його використовуєте для загальної обробки

class AdminStates(StatesGroup):
    """FSM-стани для адмін-панелі та її підрозділів."""
    admin_main = State()                # Головне адмін-меню
    user_management = State()           # Управління користувачами (список, дії)
    confirm_action = State()            # Підтвердження дії (авторизація/рівень доступу)
    set_access_level = State()          # Встановлення рівня доступу

    # Telethon управління
    telethon_management = State()       # Загальне управління Telethon
    waiting_for_telethon_input = State() # Очікування загального введення даних для Telethon операцій

    chat_matrix_management = State()    # Стан для управління чат-матрицею
    waiting_for_chat_search_query = State() # <--- НОВИЙ СТАН: Очікування вводу для пошуку чатів
    waiting_for_chat_member_id = State() # <--- НОВИЙ СТАН: Очікування ID користувача для додавання в чат