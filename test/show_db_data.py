import psycopg2

def get_schemas(cur):
    cur.execute("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY schema_name
    """)
    return [row[0] for row in cur.fetchall()]

def get_tables(cur, schema):
    cur.execute("""
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname = %s
    """, (schema,))
    return [row[0] for row in cur.fetchall()]

def get_table_comment(cur, schema, table):
    cur.execute("""
        SELECT obj_description(c.oid)
        FROM pg_class c
        WHERE c.relname = %s
          AND c.relnamespace = (
            SELECT oid FROM pg_namespace WHERE nspname = %s
          )
    """, (table, schema))
    result = cur.fetchone()
    return result[0] if result and result[0] else None

def show_tables_data(cur, schema, tables):
    for table in tables:
        # Витягуємо коментар до таблиці
        comment = get_table_comment(cur, schema, table)
        print(f"\nДані з таблиці: {schema}.{table}")
        if comment:
            print(f"Коментар: {comment}")
        else:
            print("Коментар: (немає — твій шанс додати легенду для кондиціонерів!)")
        cur.execute(f'SELECT * FROM "{schema}"."{table}"')
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        print(" | ".join(colnames))
        if rows:
            for row in rows:
                print(" | ".join(str(cell) for cell in row))
        else:
            print("Таблиця порожня, але це не біда — є куди складати кондиціонери! 😄")

def main():
    conn = psycopg2.connect("postgresql://kondiki:avrora@localhost:5432/base_bot")
    cur = conn.cursor()

    schemas = get_schemas(cur)
    print("Доступні схеми у базі:")
    for idx, schema in enumerate(schemas):
        print(f"{idx + 1}. {schema}")
    print("\nВведи номер або назву схеми, дані з якої хочеш переглянути:")
    selected_input = input("→ ").strip()

    # Дозволяємо вибір за номером або назвою
    if selected_input.isdigit():
        idx = int(selected_input) - 1
        if 0 <= idx < len(schemas):
            selected_schema = schemas[idx]
        else:
            print("Такого номера нема! Спробуй ще раз і не забудь перевірити кондиціонер 😉")
            cur.close()
            conn.close()
            return
    else:
        selected_schema = selected_input

    if selected_schema not in schemas:
        print("Такої схеми нема! Спробуй ще раз і не забудь перевірити кондиціонер 😉")
    else:
        tables = get_tables(cur, selected_schema)
        if not tables:
            print("У цій схемі таблиць нема. Можна зробити перекур! 😄")
        else:
            show_tables_data(cur, selected_schema, tables)

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()