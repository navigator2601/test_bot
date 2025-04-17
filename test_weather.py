import requests

WEATHER_API_KEY = "3fefe17fca92172c1badf79d01b0d448"  # Вставте свій API-ключ сюди
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
POLTAVA_LATITUDE = 49.554194
POLTAVA_LONGITUDE = 34.533944

def get_weather_data(latitude, longitude):
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": WEATHER_API_KEY,
        "lang": "ua",
        "units": "metric"
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Помилка отримання даних про погоду: {e}")
        return None

if __name__ == "__main__":
    weather_data = get_weather_data(POLTAVA_LATITUDE, POLTAVA_LONGITUDE)
    if weather_data:
        print("Дані про погоду для Полтави:")
        print(weather_data)
        if "weather" in weather_data and len(weather_data["weather"]) > 0:
            description = weather_data["weather"][0]["description"]
            print(f"\nОпис погоди: {description}")
        else:
            print("\nІнформація про опис погоди відсутня.")
    else:
        print("Не вдалося отримати дані про погоду.")