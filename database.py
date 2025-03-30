from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config
from datetime import datetime

engine = create_engine(Config.DB_URI)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserActionLog(Base):
    __tablename__ = 'user_action_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_user(db, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def log_user_action(db, user_id: int, action: str):
    log_entry = UserActionLog(user_id=user_id, action=action)
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry