# Файл: database/db_search_functions.py
# Призначення: Функції для взаємодії з базою даних, що стосуються пошуку.

import asyncpg
from typing import List, Dict

async def find_in_database(db_pool: asyncpg.Pool, query_text: str) -> List[Dict]:
    """
    Виконує точний пошук в базі даних, де всі слова запиту мають
    бути в одному полі.

    :param db_pool: Пул з'єднань до бази даних.
    :param query_text: Текст, який користувач ввів для пошуку.
    :return: Список словників з результатами пошуку.
    """
    try:
        search_words = [word.lower() for word in query_text.split()]
        
        # Створюємо параметри для запиту
        params = [f'%{word}%' for word in search_words]

        # Генеруємо умову WHERE, яка перевіряє наявність усіх слів в одному полі
        # Це гарантує, що "Manchester" і "24" будуть знайдені в одному полі "Модель".
        model_conditions = [f"LOWER(cmn.model_name_ukr) LIKE ${i}" for i in range(1, len(params) + 1)]
        where_clause_model = " AND ".join(model_conditions)

        # Також робимо таку ж перевірку для поля "Тип кондиціонера"
        type_conditions = [f"LOWER(ct.type_name_ukr) LIKE ${i}" for i in range(1, len(params) + 1)]
        where_clause_type = " AND ".join(type_conditions)
        
        # Об'єднуємо умови, щоб шукати або по моделі, або по типу
        where_clause = f"({where_clause_model}) OR ({where_clause_type})"
        
        sql_query = f"""
        SELECT
            cmn.model_name_ukr AS "Модель",
            ct.type_name_ukr AS "Тип кондиціонера",
            REPLACE(CONCAT(ws_cool.nominal_watt_value, ' Вт (Охолодження)'), '.', ',') AS "Потужність охолодження",
            REPLACE(CONCAT(ws_heat.nominal_watt_value, ' Вт (Обігрів)'), '.', ',') AS "Потужність обігріву",
            CONCAT_WS('/',
                REPLACE(TO_CHAR(rps.liquid_line_mm, 'FM9999999.00'), '.', ',') || 'мм',
                REPLACE(TO_CHAR(rps.gas_line_mm, 'FM9999999.00'), '.', ',') || 'мм'
            ) AS "Труби (рідина/газ)",
            rt.type_name AS "Тип холодоагенту",
            REPLACE(TRIM(LEADING ' ' FROM TO_CHAR(rc.weight_kg, 'FM0.000')) || ' кг', '.', ',') AS "Вага холодоагенту"
        FROM
            conditioners.conditioner_models cm
        LEFT JOIN
            conditioners.conditioner_model_names cmn ON cm.model_name_id = cmn.model_name_id
        LEFT JOIN
            conditioners.conditioner_types ct ON cm.conditioner_type_id = ct.conditioner_type_id
        LEFT JOIN
            conditioners.watt_specs ws_cool ON cm.cooling_watt_specs_id = ws_cool.watt_specs_id
        LEFT JOIN
            conditioners.watt_specs ws_heat ON cm.heating_watt_specs_id = ws_heat.watt_specs_id
        LEFT JOIN
            conditioners.refrigerant_pipe_specs rps ON cm.refrigerant_pipe_specs_id = rps.pipe_specs_id
        LEFT JOIN
            conditioners.refrigerant_types rt ON cm.refrigerant_type_id = rt.refrigerant_type_id
        LEFT JOIN
            conditioners.refrigerant_charges rc ON cm.refrigerant_charge_id = rc.charge_id
        WHERE
            {where_clause}
        LIMIT 10;
        """
        
        async with db_pool.acquire() as connection:
            results = await connection.fetch(sql_query, *params)
            return [dict(row) for row in results]
    except Exception as e:
        print(f"Помилка при виконанні SQL-запиту: {e}")
        return []

def format_search_results(results: List[Dict]) -> str:
    """
    Форматує результати пошуку з бази даних у зручний для читання текст.
    ... (без змін)
    """
    if not results:
        return "Нічого не знайдено."
        
    formatted_text = ""
    for idx, item in enumerate(results, 1):
        formatted_text += (
            f"**{idx}.** **{item.get('Модель', 'N/A')}**\n"
            f"   - Тип: `{item.get('Тип кондиціонера', 'N/A')}`\n"
            f"   - Охолодження: `{item.get('Потужність охолодження', 'N/A')}`\n"
            f"   - Обігрів: `{item.get('Потужність обігріву', 'N/A')}`\n"
            f"   - Труби: `{item.get('Труби (рідина/газ)', 'N/A')}`\n"
            f"   - Холодоагент: `{item.get('Тип холодоагенту', 'N/A')}` (`{item.get('Вага холодоагенту', 'N/A')}`)\n\n"
        )
    return formatted_text