from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, log_user_action

class LoggingMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update, data):
        print(f"Received update: {update}")
        with SessionLocal() as session:
            log_user_action(session, update)