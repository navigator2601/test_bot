from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import DATABASE_URL
from datetime import datetime

# Ініціалізація бази даних
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель користувача
class UserActionLog(Base):
    __tablename__ = 'user_action_log'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

def log_user_action(session: Session, update):
    username = update.message.from_user.username
    action = update.message.text
    log_entry = UserActionLog(username=username, action=action)
    session.add(log_entry)
    session.commit()

# Приклад моделі
def create_user_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()