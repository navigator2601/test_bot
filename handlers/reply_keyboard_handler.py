from aiogram import Router, types
from aiogram.filters import Text
from keyboards.reply_keyboard import create_additional_functions_keyboard, create_main_menu_keyboard

router = Router()

@router.message(Text("➡️ Додаткові функції"))
async def additional_functions_menu(message: types.Message):
    """
    Обробник для кнопки "➡️ Додаткові функції".
    Показує клавіатуру з додатковими функціями.
    """
    await message.answer(
        "Оберіть одну з додаткових функцій:",
        reply_markup=create_additional_functions_keyboard()
    )

@router.message(Text("🔙 Назад до головного меню"))
async def back_to_main_menu(message: types.Message):
    """
    Обробник для кнопки "🔙 Назад до головного меню".
    Повертає головну клавіатуру.
    """
    await message.answer(
        "Повертаємося до головного меню:",
        reply_markup=create_main_menu_keyboard()
    )