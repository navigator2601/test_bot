# database/__init__.py

# Експортуємо функції з db_pool_manager.py
from .db_pool_manager import create_db_pool, close_db_pool, get_db_pool

# Експортуємо функції з telethon_sessions_db.py
from .telethon_sessions_db import save_telethon_session, get_telethon_session, delete_telethon_session

# Експортуємо тільки ті функції, що реально існують у users_db.py
from .users_db import (
    get_user,
    add_user,
    update_user_activity,
    get_user_access_level,
    get_all_users # <--- ОТОЧОК: додайте просто назву функції, без коментарів у коді!
)