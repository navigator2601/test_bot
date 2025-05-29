# main.py
import asyncio
import logging # Хоча ми використовуємо utils.logger, цей імпорт корисний для загального розуміння
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage # Для станів FSM
from aiogram.types import BotCommand, BotCommandScopeDefault # Для встановлення команд
from aiogram.exceptions import TelegramAPIError # Для обробки помилок Telegram
from aiogram.filters import Command # Для обробки команд
from aiogram.types import Message # Для типу повідомлення
from aiogram.enums import ParseMode # Для форматування тексту

# Імпорт конфігурації (для BOT_TOKEN)
from config import BOT_TOKEN

# Імпорт нашого налаштованого логера
from utils.logger import logger # <--- Використовуємо наш логер

# --- Опис бота ---
BOT_DESCRIPTION = (
    "Вітаю, Монтажнику! Ти — частина легендарного загону “Аврора Мультимаркет” — "
    "всеукраїнської мережі магазинів, де народжуються герої кондиціонерного фронту.\n\n"
    "Я — твій цифровий напарник у Конди-Ленді, бот, створений спеціально для монтажників, "
    "які не бояться ані спеки, ані завдань під стелею.\n\n"
    "У моєму арсеналі — усе, що потрібно для монтажу без зайвих клопотів.\n"
    "Користуйся меню або кнопками — і вперед, назустріч новим установкам та кліматичним пригодам!\n"
    "Натискай /start і вперед до монтажних пригод. 💪"
)
# --- Кінець опису бота ---


async def set_default_commands(bot: Bot):
    """
    Встановлює головне меню команд для бота для ВСІХ приватних чатів.
    """
    commands = [
        BotCommand(command="start", description="Запустити бота"),
        # Додайте інші команди, якщо вони будуть у меню
        # BotCommand(command="help", description="Допомога"),
        # BotCommand(command="info", description="Інформація"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logger.info("Головне меню команд встановлено.")

@logger.catch # Додаємо декоратор для логування винятків (від loguru, але можемо реалізувати свою обробку)
async def handle_start(message: Message):
    """
    Обробник команди /start.
    Привітає користувача та надішле опис бота.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    logger.info(f"Отримано команду /start від користувача: ID={user_id}, Username={username}, Name={first_name}.")

    await message.answer(
        text=BOT_DESCRIPTION,
        parse_mode=ParseMode.MARKDOWN_V2 # Вказуємо, що використовуємо Markdown V2
    )
    logger.info(f"Надіслано привітання та опис боту користувачу {user_id}.")

async def main():
    """
    Головна функція, яка ініціалізує та запускає бота.
    """
    logger.info("Починаю ініціалізацію бота...")

    # Ініціалізація сховища FSM (для управління станами користувачів)
    storage = MemoryStorage()

    # Створення об'єкта бота
    bot = Bot(token=BOT_TOKEN)
    logger.info("Об'єкт Bot створено.")

    # Створення об'єкта диспетчера
    dp = Dispatcher(storage=storage)
    logger.info("Об'єкт Dispatcher створено.")

    # Реєстрація обробників
    dp.message.register(handle_start, Command("start")) # Реєструємо обробник для команди /start
    logger.info("Обробник команди /start зареєстровано.")

    # Встановлення команд для бота в меню Telegram
    await set_default_commands(bot)

    logger.info("Бот запущено. Починаю polling...")

    try:
        # Запускаємо polling (обробку вхідних оновлень)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критична помилка під час роботи бота: {e}", exc_info=True)
    finally:
        # Закриваємо сесію бота при зупинці
        await bot.session.close()
        logger.info("Бот зупинено, сесію закрито.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено вручну (Ctrl+C).")
    except ValueError as e:
        logger.critical(f"Помилка конфігурації: {e}")
    except Exception as e:
        logger.critical(f"Непередбачена критична помилка запуску бота: {e}", exc_info=True)