# Файл: database/db_search_functions.py
# Призначення: Функції для взаємодії з базою даних, що стосуються пошуку та каталогу.

import asyncpg
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

async def find_in_database(db_pool: asyncpg.Pool, query_text: str) -> List[Dict]:
    """
    Виконує точний пошук в базі даних, де всі слова запиту мають
    бути в одному полі.
    """
    query_file_path = "database/sql_queries/search_query.sql"
    try:
        with open(query_file_path, 'r', encoding='utf-8') as f:
            sql_query = f.read()
    except FileNotFoundError:
        logger.error(f"SQL-файл не знайдено за шляхом: {query_file_path}")
        return []

    try:
        search_words = [word.lower() for word in query_text.split()]
        params = [f'%{word}%' for word in search_words]

        async with db_pool.acquire() as connection:
            results = await connection.fetch(sql_query, *params)
            return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Помилка при виконанні SQL-запиту пошуку: {e}", exc_info=True)
        return []

def format_search_results(results: List[Dict]) -> str:
    """
    Форматує результати пошуку з бази даних у зручний для читання текст.
    """
    if not results:
        return "Нічого не знайдено."
        
    formatted_text = ""
    for idx, item in enumerate(results, 1):
        formatted_text += (
            f"**{idx}.** **{item.get('Модель', 'N/A')}**\n"
            f"   - Тип: `{item.get('Тип кондиціонера', 'N/A')}`\n"
            f"   - Бренд: `{item.get('Бренд', 'N/A')}`\n"
            f"   - Охолодження: `{item.get('Потужність охолодження', 'N/A')}` Вт\n"
            f"   - Обігрів: `{item.get('Потужність обігріву', 'N/A')}` Вт\n"
            f"   - Розмір труб: `{item.get('Розміри труб', 'N/A')}`\n"
            f"   - Фреон: `{item.get('Тип фреону', 'N/A')}`\n"
            f"   - Заправка: `{item.get('Заправка фреоном', 'N/A')}` г\n\n"
        )
    return formatted_text

async def get_brands_with_model_count(db_pool: asyncpg.Pool) -> List[Dict]:
    """
    Виконує SQL-запит для отримання списку брендів з кількістю моделей.
    """
    query_file_path = "database/sql_queries/get_brands_with_model_count.sql"
    try:
        with open(query_file_path, 'r', encoding='utf-8') as f:
            sql_query = f.read()
    except FileNotFoundError:
        logger.error(f"SQL-файл не знайдено за шляхом: {query_file_path}")
        return []

    async with db_pool.acquire() as conn:
        results = await conn.fetch(sql_query)
        return [dict(r) for r in results]

async def get_models_by_brand(db_pool: asyncpg.Pool, brand_id: int) -> List[Dict]:
    """
    Виконує SQL-запит для отримання списку моделей за ID бренду.
    """
    query_file_path = "database/sql_queries/get_models_by_brand.sql"
    try:
        with open(query_file_path, 'r', encoding='utf-8') as f:
            sql_query = f.read()
    except FileNotFoundError:
        logger.error(f"SQL-файл не знайдено за шляхом: {query_file_path}")
        return []
    
    async with db_pool.acquire() as conn:
        try:
            results = await conn.fetch(sql_query, brand_id)
            return [dict(r) for r in results]
        except Exception as e:
            logger.error(f"Помилка при виконанні SQL-запиту: {e}", exc_info=True)
            return []

async def get_model_details_by_id(db_pool: asyncpg.Pool, model_id: int) -> Dict | None:
    """
    Виконує SQL-запит для отримання повної інформації про модель за її ID.
    """
    query_file_path = "database/sql_queries/get_model_details_by_id.sql"
    try:
        with open(query_file_path, 'r', encoding='utf-8') as f:
            sql_query = f.read()
    except FileNotFoundError:
        logger.error(f"SQL-файл не знайдено за шляхом: {query_file_path}")
        return None

    async with db_pool.acquire() as conn:
        try:
            result = await conn.fetchrow(sql_query, model_id)
            return dict(result) if result else None
        except Exception as e:
            logger.error(f"Помилка при отриманні деталей моделі з ID {model_id}: {e}", exc_info=True)
            return None

def format_model_details(model_details: Dict) -> str:
    """
    Форматує словник з деталями моделі в зручний для читання текст.
    """
    if not model_details:
        return "Деталі моделі не знайдено."
    
    text = (
        f"<b>🔍 Деталі моделі {model_details.get('brand_name', 'N/A')} {model_details.get('model_name', 'N/A')}</b>\n\n"
        f"⚡️ <b>Характеристики:</b>\n"
        f"❄️ Охолодження: {model_details.get('cooling_capacity', 'N/A')} Вт\n"
        f"🔥 Обігрів: {model_details.get('heating_capacity', 'N/A')} Вт\n"
        f"📏 Розміри труб: {model_details.get('pipe_specs', 'N/A')}\n"
        f"🧪 Тип фреону: {model_details.get('refrigerant_type', 'N/A')}\n"
        f"⚖️ Заправка фреону: {model_details.get('refrigerant_charge', 'N/A')} г\n"
    )
    return text