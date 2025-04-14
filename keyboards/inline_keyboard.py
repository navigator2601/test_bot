from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_brands_inline_keyboard(brands):
    """
    Створює інлайн-клавіатуру зі списком брендів.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)  # Два бренди в одному рядку
    
    for brand in brands:
        brand_name = brand["brand_name"]
        model_count = brand["model_count"]
        button_text = f"{brand_name} ({model_count})"
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"brand_{brand_name}"))
    
    return keyboard