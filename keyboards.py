from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/start"))
    keyboard.add(KeyboardButton("/user"))
    return keyboard