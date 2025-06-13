# common/states.py
from aiogram.fsm.state import State, StatesGroup

class MenuStates(StatesGroup):
    """FSM-стани для головного меню."""
    main_menu = State()
    any = State() # <--- ЄДИНА ДОДАНА ЗМІНА: Додано стан 'any'

class AdminStates(StatesGroup):
    """FSM-стани для адмін-панелі та її підрозділів, включаючи Telethon авторизацію."""
    admin_main = State()              # Головне адмін-меню
    user_management = State()         # Управління користувачами (список, дії)
    confirm_action = State()          # Підтвердження дії (авторизація/рівень доступу)
    set_access_level = State()        # Встановлення рівня доступу

    # Telethon авторизація та управління
    telethon_management = State()     # Загальне управління Telethon
    waiting_for_phone_number = State() # Очікування номера телефону для Telethon авторизації
    waiting_for_code = State()         # Очікування коду авторизації Telethon
    waiting_for_2fa_password = State() # Очікування 2FA пароля Telethon
    waiting_for_telethon_input = State() # Очікування загального введення даних для Telethon (для інших функцій, як отримати інфо, приєднатись)

    chat_matrix_management = State()  # НОВИЙ СТАН: Стан для управління чат-матрицею