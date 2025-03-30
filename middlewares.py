from aiogram.dispatcher.middlewares.base import BaseMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, log_user_action

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        print(f"Received update: {event}")
        with SessionLocal() as session:
            log_user_action(session, event)
        return await handler(event, data)