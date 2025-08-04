import psycopg2

def get_tables(cur, schema):
    cur.execute("""
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname = %s
    """, (schema,))
    tables = [row[0] for row in cur.fetchall()]
    return tables

def show_schema_structure(cur, schema):
    tables = get_tables(cur, schema)
    if not tables:
        print("У схемі таблиць немає. Можна перепочити, Віталію! 😄")
    for table in tables:
        print("----------------------------------------")
        print(f"Знайдена таблиця: {schema}.{table}")

        # Коментар до таблиці
        cur.execute("""
            SELECT obj_description(c.oid)
            FROM pg_class c
            WHERE c.relname = %s
              AND c.relnamespace = (
                SELECT oid FROM pg_namespace WHERE nspname = %s
              )
        """, (table, schema))
        result = cur.fetchone()
        comment = result[0] if result and result[0] else None
        print(f"Знайдено коментар: {comment if comment else '(немає)'}")

        # Стовпці через pg_catalog
        cur.execute("""
            SELECT a.attname, t.typname, NOT a.attnotnull as is_nullable, a.atthasdef as has_default, d.description
            FROM pg_catalog.pg_attribute a
            JOIN pg_catalog.pg_class c ON a.attrelid = c.oid
            JOIN pg_catalog.pg_type t ON a.atttypid = t.oid
            LEFT JOIN pg_catalog.pg_description d ON d.objoid = c.oid AND d.objsubid = a.attnum
            JOIN pg_catalog.pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relname = %s AND n.nspname = %s
              AND a.attnum > 0 AND NOT a.attisdropped
            ORDER BY a.attnum
        """, (table, schema))
        columns = cur.fetchall()

        print("Знайдено стовпці:")
        for col in columns:
            name = col[0]
            dtype = col[1]
            nullable = 'NULL' if col[2] else 'NOT NULL'
            has_default = 'default' if col[3] else ''
            col_comment = col[4] if col[4] else ''
            print(f"    {name} ({dtype}, {nullable}, {has_default}) [{col_comment}]")

        # Зовнішні ключі
        cur.execute("""
            SELECT kcu.column_name, ccu.table_name, ccu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
              ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = %s AND tc.table_name = %s;
        """, (schema, table))
        fks = cur.fetchall()
        print("Знайдено зовнішні ключі:")
        if fks:
            for fk in fks:
                col, ref_table, ref_col = fk
                print(f"  {col} → {ref_table}.{ref_col}")
        else:
            print("  (немає)")
def main():
    conn = psycopg2.connect("postgresql://kondiki:avrora@localhost:5432/base_bot")
    cur = conn.cursor()

    cur.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schema_name
    """)
    schemas = [row[0] for row in cur.fetchall()]
    print("Доступні схеми у базі:")
    for idx, schema in enumerate(schemas):
        print(f"{idx + 1}. {schema}")
    print("\nВведи номер або назву схеми, структуру якої хочеш побачити:")
    selected_input = input("→ ").strip()

    if selected_input.isdigit():
        idx = int(selected_input) - 1
        if 0 <= idx < len(schemas):
            selected_schema = schemas[idx]
        else:
            print("Такого номера нема! Спробуй ще раз — і не забувай про кондиціонери 😉")
            cur.close()
            conn.close()
            return
    else:
        selected_schema = selected_input

    if selected_schema not in schemas:
        print("Такої схеми нема! Спробуй ще раз і не забувай перевірити кондиціонер 😉")
    else:
        show_schema_structure(cur, selected_schema)

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()