# відносний шлях до файлу: database/db_search_functions.py
# Призначення: Функції для взаємодії з базою даних, що стосуються пошуку.

import asyncpg
from typing import List, Dict, Optional
import aiofiles
import os

async def get_all_brands_with_count(db_pool: asyncpg.Pool) -> List[Dict]:
    """
    Виконує запит до БД для отримання списку брендів, які мають моделі,
    разом з кількістю моделей для кожного бренду.
    
    :param db_pool: Пул з'єднань до бази даних.
    :return: Список словників з брендами та кількістю моделей.
    """
    try:
        # Шлях до файлу - відносно кореня проєкту.
        file_path = os.path.join('database', 'sql_queries', 'get_brands_with_model_count.sql')
        
        # ВИКОРИСТОВУЄМО АСИНХРОННЕ ЧИТАННЯ ФАЙЛУ
        async with aiofiles.open(file_path, mode='r') as file:
            sql_query = await file.read()

        async with db_pool.acquire() as connection:
            results = await connection.fetch(sql_query)
            # Перетворюємо об'єкти asyncpg.Record у словники для зручності
            return [dict(row) for row in results]
    except FileNotFoundError:
        print(f"Помилка: Файл SQL-запиту '{file_path}' не знайдено. Перевірте шлях.")
        return []
    except Exception as e:
        print(f"Помилка при виконанні запиту на отримання брендів: {e}")
        return []

async def get_models_by_brand(db_pool: asyncpg.Pool, brand_name: str) -> List[Dict]:
    """
    Отримує список моделей для конкретного бренду.
    """
    try:
        file_path = os.path.join('database', 'sql_queries', 'get_models_by_brand.sql')
        
        async with aiofiles.open(file_path, mode='r') as file:
            sql_query = await file.read()

        async with db_pool.acquire() as connection:
            results = await connection.fetch(sql_query, brand_name)
            return [dict(row) for row in results]
    except FileNotFoundError:
        print(f"Помилка: Файл SQL-запиту '{file_path}' не знайдено. Перевірте шлях.")
        return []
    except Exception as e:
        print(f"Помилка при отриманні моделей для бренду '{brand_name}': {e}")
        return []

async def get_model_details_by_id(db_pool: asyncpg.Pool, model_id: int) -> Optional[Dict]:
    """
    Отримує повну інформацію про конкретну модель за її ID.
    """
    try:
        file_path = os.path.join('database', 'sql_queries', 'get_model_details_by_id.sql')

        async with aiofiles.open(file_path, mode='r') as file:
            sql_query = await file.read()

        async with db_pool.acquire() as connection:
            result = await connection.fetchrow(sql_query, model_id)
            if result:
                return dict(result)
            return None
    except FileNotFoundError:
        print(f"Помилка: Файл SQL-запиту '{file_path}' не знайдено. Перевірте шлях.")
        return None
    except Exception as e:
        print(f"Помилка при отриманні деталей моделі з ID {model_id}: {e}")
        return None