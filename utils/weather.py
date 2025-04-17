import requests
from config import WEATHER_API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
LOCATION = "Poltava,UA"

def get_weather():
    """
    Отримує поточну погоду для Полтави з OpenWeather API.
    """
    params = {
        "q": LOCATION,
        "appid": WEATHER_API_KEY,
        "lang": "ua",
        "units": "metric"
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Помилка під час отримання даних про погоду: {e}")
        return None