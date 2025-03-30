from database import get_db_connection

def save_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
    conn.commit()
    cursor.close()
    conn.close()