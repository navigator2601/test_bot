import logging
from aiogram import Router, types
from keyboards.inline_keyboard import get_brands_inline_keyboard
from database.db import get_brands

router = Router()
logger = logging.getLogger(__name__)

@router.message(lambda message: message.text == "🛍️ Каталог")
async def catalog_handler(message: types.Message):
    try:
        # Отримуємо список брендів із бази даних
        brands = await get_brands()
        
        if not brands:
            await message.answer("На жаль, зараз немає доступних брендів. Спробуйте пізніше.")
            return
        
        # Створюємо інлайн-клавіатуру
        keyboard = get_brands_inline_keyboard(brands)
        
        # Відправляємо повідомлення з клавіатурою
        await message.answer("Виберіть бренд зі списку нижче:", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Помилка в обробнику 'Каталог': {e}")
        await message.answer("Сталася помилка. Спробуйте пізніше.")