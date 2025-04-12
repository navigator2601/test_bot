from aiogram import types, Router, F
from keyboards import main_menu, catalog_menu

router = Router()

# Обробник для кнопки "📚 Каталог"
@router.message(F.text == "📚 Каталог")
async def show_catalog_menu(message: types.Message):
    """Показує підменю для кнопки Каталог"""
    await message.answer(
        "Оберіть дію з меню нижче:",
        reply_markup=catalog_menu()  # Показує компактне підменю для "Каталогу"
    )

# Обробники для підменю каталогу
@router.message(F.text == "📜 Вибір зі списку")
async def choose_from_list(message: types.Message):
    """Обробник для кнопки 'Вибір зі списку'"""
    await message.answer("Ви обрали 'Вибір зі списку'. Тут буде список доступного обладнання.")

@router.message(F.text == "🔍 Пошук по бренду")
async def search_by_brand(message: types.Message):
    """Обробник для кнопки 'Пошук по бренду'"""
    await message.answer("Введіть назву бренду, який вас цікавить.")

@router.message(F.text == "📂 Пошук по типу")
async def search_by_type(message: types.Message):
    """Обробник для кнопки 'Пошук по типу'"""
    await message.answer("Оберіть тип обладнання, який вас цікавить.")

# Обробник для кнопки "⬅️ Назад"
@router.message(F.text == "⬅️ Назад")
async def back_to_main_menu(message: types.Message):
    """Повернення до головного меню"""
    await message.answer(
        "Повертаємося до головного меню:",
        reply_markup=main_menu()  # Показує головне меню
    )