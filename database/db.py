import asyncpg
import logging

# Налаштування підключення до бази даних
DATABASE_URL = "postgresql://neondb_owner:npg_dhwrDX6O1keB@ep-round-star-a9r38wl3-pooler.gwc.azure.neon.tech/neondb"

async def get_brands():
    """
    Отримує список брендів і кількість моделей для кожного бренду.
    """
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        query = """
        SELECT 
            b.name AS brand_name, 
            COUNT(m.id) AS model_count
        FROM 
            brands b
        INNER JOIN 
            models m 
        ON 
            b.id = m.brand_id
        GROUP BY 
            b.name
        ORDER BY 
            model_count DESC;
        """
        
        rows = await conn.fetch(query)
        await conn.close()
        
        return rows
    except Exception as e:
        logging.error(f"Помилка при отриманні списку брендів: {e}")
        return []