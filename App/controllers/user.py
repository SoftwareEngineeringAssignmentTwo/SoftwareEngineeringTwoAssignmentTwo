from App.models import User
from App.database import db

def create_user(username, password):
    newuser = User(username=username, password=password)
    try: 
        db.session.add(newuser)
        db.session.commit()
        return newuser
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return None

def create_staff(username, password):
    newstaff = User(username=username, password=password)
    try:
        db.session.add(newstaff)
        db.session.commit()
        return newstaff
    except Exception as e:
        db.session.rollback()
        print(f"Error creating staff user: {e}")
        return None

def create_student(username, password):
    newstudent = User(username=username, password=password)
    try:
        db.session.add(newstudent)
        db.session.commit()
        return newstudent
    except Exception as e:
        db.session.rollback()
        print(f"Error creating student user: {e}")              
        return None

def get_user_by_username(username):
    result = db.session.execute(db.select(User).filter_by(username=username))
    return result.scalar_one_or_none()

def get_user(id):
    return db.session.get(User, id)

def get_all_users():
    return db.session.scalars(db.select(User)).all()

def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        # user is already in the session; no need to re-add
        db.session.commit()
        return True
    return None
