# common/__init__.py

from .constants import ACCESS_LEVEL_BUTTONS, ALL_MENU_BUTTONS, BUTTONS_PER_PAGE
from .messages import get_access_level_description, get_random_admin_welcome_message
# from .telethon_states import TelethonAuthStates # <--- ЦЕЙ РЯДОК МАЄ БУТИ ВИДАЛЕНИЙ АБО ЗАКОМЕНТОВАНИЙ
from .states import MenuStates, AdminStates # <--- ДОДАНО ІМПОРТ AdminStates та MenuStates