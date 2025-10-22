# Файл: database/db_admin_functions.py (Створення/оновлення функції)

from asyncpg import Pool
from typing import List, Dict
import random # Тільки для імітації

# Приклад імітації функції, яку ви маєте реалізувати
async def get_brands_and_series_with_fill_percent(db_pool: Pool) -> List[Dict]:
    """
    Отримує з БД список усіх брендів/серій з розрахунком % наповнення даних
    (наприклад, наявність усіх обов'язкових полів для моделей в цій серії).
    
    Повертає список: [{'name': 'Бренд', 'series_name': 'Серія', 'fill_percent': 75, 'brand_id': 1}, ...]
    """
    
    # 🔥🔥🔥 ЗАГЛУШКА: Замініть цей блок на реальний запит до БД 🔥🔥🔥
    logger.warning("Використовується заглушка get_brands_and_series_with_fill_percent. Потрібна реалізація.")
    
    data = [
        {'name': 'Gree', 'series_name': 'Bora', 'fill_percent': random.randint(50, 100), 'brand_id': 1},
        {'name': 'Daikin', 'series_name': 'FTX', 'fill_percent': random.randint(50, 100), 'brand_id': 2},
        {'name': 'Mitsubishi', 'series_name': 'Heavy', 'fill_percent': random.randint(10, 50), 'brand_id': 3},
        {'name': 'Cooper&Hunter', 'series_name': 'Veritas', 'fill_percent': random.randint(80, 100), 'brand_id': 4},
        {'name': 'Gree', 'series_name': 'Lomo', 'fill_percent': random.randint(10, 90), 'brand_id': 5},
    ]
    # 🔥🔥🔥 КІНЕЦЬ ЗАГЛУШКИ 🔥🔥🔥
    
    return data