from aiogram import Router, types, Bot
from aiogram.types import BotCommand
from aiogram.filters import Command
from utils.logger import get_logger  # Логер для відстеження подій

# Ініціалізація логера
logger = get_logger(__name__)

# Ініціалізація роутера
router = Router()

# Функція для встановлення головного меню команд
async def set_main_menu(bot: Bot):
    """
    Встановлює головне меню команд для бота.
    """
    commands = [
        BotCommand(command="/start", description="Почати роботу з ботом"),
        BotCommand(command="/help", description="Список доступних команд"),
        BotCommand(command="/info", description="Інформація про бота"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Головне меню команд встановлено.")

# Обробник команди /help
@router.message(Command(commands=["help"]))
async def help_command_handler(message: types.Message):
    """
    Обробник команди /help.
    """
    help_text = (
        "Доступні команди:\n"
        "/start - Почати роботу з ботом\n"
        "/help - Список доступних команд\n"
        "/info - Інформація про бота\n"
    )
    await message.answer(help_text)
    logger.info(f"Користувач {message.from_user.username or message.from_user.first_name} виконав команду /help.")

# Обробник команди /info
@router.message(Command(commands=["info"]))
async def info_command_handler(message: types.Message):
    """
    Обробник команди /info.
    """
    info_text = (
        "Цей бот створений для тестових цілей.\n"
        "Він може виконувати різноманітні дії, залежно від ваших потреб.\n"
        "Автор: Віталій @navigator2601.\n"
    )
    await message.answer(info_text)
    logger.info(f"Користувач {message.from_user.username or message.from_user.first_name} виконав команду /info.")

# Функція реєстрації обробників у диспетчері
def register_menu_handlers(dp):
    """
    Реєструє всі обробники, пов'язані з меню.
    """
    dp.include_router(router)