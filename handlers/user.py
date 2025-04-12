from aiogram import types, Router, F
from keyboards import main_menu, catalog_menu
from database import get_brands_with_model_counts

router = Router()

# Обробник для кнопки "📚 Каталог"
@router.message(F.text == "📚 Каталог")
async def show_catalog_menu(message: types.Message):
    """
    Показує список брендів, які мають моделі.
    """
    brands = await get_brands_with_model_counts()
    if not brands:
        await message.answer("На жаль, поки що немає доступних брендів.")
    else:
        await message.answer(
            "Виберіть бренд зі списку:",
            reply_markup=catalog_menu(brands)
        )

# Обробник для кнопки "⬅️ Назад"
@router.message(F.text == "⬅️ Назад")
async def back_to_main_menu(message: types.Message):
    """
    Повернення до головного меню.
    """
    await message.answer(
        "Повертаємося до головного меню:",
        reply_markup=main_menu()
    )