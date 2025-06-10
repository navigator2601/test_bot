# common/states.py
from aiogram.fsm.state import State, StatesGroup

class MenuStates(StatesGroup):
    """FSM-стани для головного меню."""
    main_menu = State()
    any = State() # <--- ЄДИНА ДОДАНА ЗМІНА: Додано стан 'any'

class AdminStates(StatesGroup):
    """FSM-стани для адмін-панелі та її підрозділів."""
    admin_main = State()             # Головне адмін-меню
    user_management = State()        # Управління користувачами (список, дії)
    confirm_action = State()         # Підтвердження дії (авторизація/рівень доступу)
    set_access_level = State()       # Встановлення рівня доступу
    telethon_management = State()    # Управління Telethon
    waiting_for_telethon_input = State() # Очікування введення даних для Telethon (телефон, код, посилання)
    chat_matrix_management = State() # НОВИЙ СТАН: Стан для управління чат-матрицею