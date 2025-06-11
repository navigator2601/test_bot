# common/telethon_states.py

from aiogram.fsm.state import StatesGroup, State

class TelethonAuthStates(StatesGroup):
    """FSM-стани для процесу авторизації Telethon."""
    waiting_for_phone_number = State()
    waiting_for_code = State()
    waiting_for_2fa_password = State()