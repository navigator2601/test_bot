from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply_keyboard import create_main_menu_keyboard  # Імпортуємо клавіатуру
from utils.last_login import log_user_login
from utils.logger import logger  # Імпортуємо основний логер
from datetime import datetime
import random
import asyncio
import requests
from config import WEATHER_API_KEY  # Імпортуємо ключ API для погоди

# Ініціалізація маршрутизатора
router = Router()


def get_weather():
    """
    Отримує дані про погоду для міста Полтава через API OpenWeatherMap.
    """
    city = "Poltava"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=uk"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Не вдалося отримати погоду. Код помилки: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Помилка під час запиту до API погоди: {e}")
        return None


def get_season():
    """
    Визначає поточну пору року залежно від дати.
    """
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "winter"  # Зима
    elif month in [3, 4, 5]:
        return "spring"  # Весна
    elif month in [6, 7, 8]:
        return "summer"  # Літо
    elif month in [9, 10, 11]:
        return "autumn"  # Осінь


def generate_greeting(first_name, weather_data):
    """
    Генерує привітання користувачу з урахуванням часу доби, сезону та погоди.
    """
    # Визначення часу доби
    now = datetime.now()
    hour = now.hour
    if 5 <= hour < 12:
        time_phrases = [
            "Доброго ранку! Бажаю чудового початку дня.",
            "З першими променями сонця вітаю вас!",
            "Прокидайтеся! Новий день, нові можливості.",
            "Ранкова свіжість вітає! Чим можу допомогти?",
            "Вдалого ранку! Нехай усе вдається."
        ]
    elif 12 <= hour < 18:
        time_phrases = [
            "Доброго дня! Сподіваюся, у вас все добре.",
            "Сонячного дня! Готовий до ваших запитів.",
            "Вітаю в розпалі дня!",
            "Теплого дня! Чим можу бути корисним?",
            "Гарного дня! Якщо потрібна допомога - звертайтесь."
        ]
    elif 18 <= hour < 23:
        time_phrases = [
            "Доброго вечора! Затишку вам цієї весни.",
            "Приємного вечора! Сподіваюся, день був вдалим.",
            "Вечірнє вітання! Готовий допомогти з кліматом.",
            "Комфортного завершення дня!",
            "Вітаю з настанням вечора! Як пройшов ваш день?"
        ]
    else:
        time_phrases = [
            "Доброї ночі! Нехай ваш сон буде міцним.",
            "Тихої ночі! До завтра.",
            "Вітаю в нічний час! Якщо щось термінове - пишіть.",
            "Солодких снів! Відпочивайте.",
            "На добраніч! До нових зустрічей."
        ]

    # Рандомізоване привітання
    greeting = random.choice(time_phrases)

    # Привітання для поточної пори року
    season = get_season()
    seasonal_phrases = {
        "spring": [
            "Весна в Полтаві чарівна!",
            "Насолоджуйтесь весняним теплом!",
            "Весна - час оновлення!",
            "Квітне весна!",
            "Весняний настрій у кожен дім!"
        ],
        "summer": [
            "Літо в самому розпалі! Нехай сонце завжди світить у вашому серці!",
            "Спекотне привітання цього чудового літнього дня!",
            "Насолоджуйтесь теплом та яскравими днями літа!",
            "Літо – час для відпочинку та натхнення!",
            "Сонячного настрою цього літнього дня!"
        ],
        "autumn": [
            "Осінь прийшла, а з нею – золоті барви природи!",
            "Затишного осіннього дня! Нехай тепло буде у вашому серці.",
            "Вітання в осінню пору! Час для гарячого чаю і гарних розмов.",
            "Осінь – це час для роздумів і нових ідей!",
            "Нехай ця осінь подарує вам нові пригоди та яскраві дні!"
        ],
        "winter": [
            "Зимове вітання! Нехай ваш день буде таким же білим і чарівним, як сніг.",
            "Затишного зимового вечора! Мерщій до чаю з теплим пледом!",
            "Зима – час для казок! Нехай ваш день буде казковим.",
            "Холод за вікном, але тепло у серці – ось зимове вітання від мене.",
            "Нехай зимові дні принесуть вам радість і натхнення!"
        ]
    }
    seasonal_message = random.choice(seasonal_phrases[season])

    # Погодні умови
    if weather_data:
        weather_description = weather_data["weather"][0]["description"]
        temp = weather_data["main"]["temp"]
        weather_phrases = f"Зараз у Полтаві {weather_description}, температура {temp}°C."
    else:
        weather_phrases = "На жаль, не вдалося отримати дані про погоду."

    return f"{greeting}\n{seasonal_message}\n{weather_phrases}\nРадий вас бачити, {first_name}!"


def generate_extra_message():
    """
    Генерує додаткове повідомлення.
    """
    extra_messages = [
        "Скористайтеся меню внизу, або просто напиши що тебе бентежить.",
        "В меню внизу є всі необхідні кнопки. Якщо не можете щось знайти напишіть.",
        "В моїй базі багато інформації, перегляньте меню або пришліть повідомлення.",
        "Якщо вас бентежить меню внизу, просто напишіть що вас цікавить.",
        "Що б не сталося, ви можете знайти все у меню знизу. Якщо це складно, то пришліть повідомлення."
    ]
    return random.choice(extra_messages)


@router.message(F.text == "/start")
async def start_command(message: Message):
    full_name = f"{message.from_user.first_name} {message.from_user.last_name}".strip()
    username = message.from_user.username

    # Логування входу користувача в last_login.log
    log_user_login(
        user_id=message.from_user.id,
        username=username,
        full_name=full_name
    )

    # Логування дій користувача в bot.log
    logger.info(
        f"Користувач {full_name} (@{username}) (ID: {message.from_user.id}) виконав команду /start."
    )

    # Отримання даних про погоду
    weather_data = get_weather()

    # Генерація привітання
    greeting_message = generate_greeting(message.from_user.first_name, weather_data)
    extra_message = generate_extra_message()

    # Відправка індикатора набору тексту
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(1)  # Затримка для більш реалістичного ефекту
    await message.bot.send_message(chat_id=message.chat.id, text=greeting_message, reply_markup=create_main_menu_keyboard())

    # Відправка індикатора набору тексту перед другим повідомленням
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(1)  # Затримка для більш реалістичного ефекту
    await message.bot.send_message(chat_id=message.chat.id, text=extra_message, reply_markup=create_main_menu_keyboard())