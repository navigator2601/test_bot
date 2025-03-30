from database import SessionLocal, UserActionLog

def save_user(username):
    session = SessionLocal()
    try:
        # Створюємо новий запис користувача
        new_user_action = UserActionLog(username=username, action="joined")
        session.add(new_user_action)
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()