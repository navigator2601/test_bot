from datetime import datetime

def get_greeting():
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return "Доброго ранку"
    elif 12 <= current_hour < 18:
        return "Доброго дня"
    elif 18 <= current_hour < 22:
        return "Доброго вечора"
    else:
        return "Доброї ночі"
