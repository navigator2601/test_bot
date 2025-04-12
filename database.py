import asyncpg
from config import DB_URL

# Пул з'єднань з базою даних
pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(dsn=DB_URL)

async def get_brands_with_model_counts():
    """
    Отримує список брендів та кількість моделей для кожного бренду.
    Повертає список у форматі [(brand_name, model_count), ...].
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT b.name, COUNT(m.id) AS model_count
            FROM brands b
            JOIN models m ON b.id = m.brand_id
            GROUP BY b.id
            ORDER BY b.name
        """)
        return [(row["name"], row["model_count"]) for row in rows]