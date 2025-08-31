# Файл: common/states.py
# Призначення: Визначення FSM-станів для різних частин бота.
# Стани дозволяють боту "пам'ятати" поточний етап взаємодії з користувачем.

from aiogram.fsm.state import State, StatesGroup

class MenuStates(StatesGroup):
    """FSM-стани для головного меню."""
    main_menu = State()
    any = State()
    
    # Стан, коли бот очікує вводу для пошуку
    find = State()

class CatalogStates(StatesGroup):
    """Стани для роботи з каталогом кондиціонерів."""
    search = State()
    brand_selection = State()
    model_selection = State()
    model_info = State()

class AdminStates(StatesGroup):
    """FSM-стани для адмін-панелі та її підрозділів."""
    admin_main = State()
    user_management = State()
    confirm_action = State()
    set_access_level = State()
    
    telethon_management = State()
    waiting_for_telethon_input = State()
    
    chat_matrix_management = State()
    waiting_for_chat_search_query = State()
    waiting_for_chat_member_id = State()