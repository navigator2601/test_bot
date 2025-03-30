from aiogram import BaseMiddleware
from aiogram.types import Update
from sqlalchemy.orm import Session
from database import SessionLocal, log_user_action

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        db: Session = SessionLocal()
        if event.message:
            user_id = event.message.from_user.id
            action = event.message.text
            log_user_action(db, user_id, action)
        print(f"Received event: {event}")
        return await handler(event, data)