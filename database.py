import psycopg2
from config import DATABASE_DSN

def connect_db():
    """Підключення до бази даних"""
    return psycopg2.connect(dsn=DATABASE_DSN)
