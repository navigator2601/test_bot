from database import connect_db

def fetch_brands():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
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
    """)
    brands = cur.fetchall()
    conn.close()
    return brands

def fetch_types(brand_name):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            t.name AS type_name, 
            COUNT(m.id) AS model_count
        FROM 
            types t
        INNER JOIN 
            models m 
        ON 
            t.id = m.type_id
        INNER JOIN 
            brands b
        ON 
            b.id = m.brand_id
        WHERE 
            b.name = %s
        GROUP BY 
            t.name
        ORDER BY 
            model_count DESC;
    """, (brand_name,))
    types = cur.fetchall()
    conn.close()
    return types
