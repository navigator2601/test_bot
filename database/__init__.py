# database/__init__.py

# Експортуємо функції з db_pool_manager.py
from .db_pool_manager import create_db_pool, close_db_pool, get_db_pool

# Експортуємо функції з telethon_sessions_db.py
from .telethon_sessions_db import save_telethon_session, get_telethon_session, delete_telethon_session

# Експортуємо функції з telethon_chats_db.py <--- НОВИЙ РЯДОК
from . import telethon_chats_db # <--- НОВИЙ РЯДОК: Імпортуємо весь модуль, щоб використовувати telethon_chats_db.add_allowed_chat тощо

# Експортуємо тільки ті функції, що реально існують у users_db.py
from .users_db import (
    get_user,
    add_user,
    update_user_activity,
    get_user_access_level,
    get_all_users
)