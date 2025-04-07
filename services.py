from database import SessionLocal, UserActionLog

def save_user(username):
    db = SessionLocal()
    user_action = UserActionLog(username=username)
    db.add(user_action)
    db.commit()
    db.close()