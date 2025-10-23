from App.models import User, Student, Staff
from App.database import db
from sqlalchemy import insert

def create_user(username, password, user_type=None):
    """Create a user. If user_type is 'student' or 'staff' create the appropriate subclass."""
    # If username already exists, return the existing user instead of attempting to insert a duplicate
    existing = get_user_by_username(username)
    if existing:
        return existing

    if user_type == 'student':
        newuser = Student(username=username, password=password)
    elif user_type == 'staff':
        newuser = Staff(username=username, password=password)
    else:
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
    existing = get_user_by_username(username)
    if existing:
        # If the existing user is already staff, return it
        if existing.user_type == 'staff':
            return existing
        # Convert existing plain user into staff by inserting into staff table
        try:
            db.session.execute(insert(Staff.__table__).values(staffID=existing.userID))
            existing.user_type = 'staff'
            db.session.commit()
            # Return the user as a Staff instance
            return db.session.get(User, existing.userID)
        except Exception as e:
            db.session.rollback()
            print(f"Error converting existing user to staff: {e}")
            return None
    # No existing user, create new staff
    newstaff = Staff(username=username, password=password)
    try:
        db.session.add(newstaff)
        db.session.commit()
        return newstaff
    except Exception as e:
        db.session.rollback()
        print(f"Error creating staff user: {e}")
        return None

def create_student(username, password):
    existing = get_user_by_username(username)
    if existing:
        if existing.user_type == 'student':
            return existing
        # Convert existing plain user into student by inserting into student table
        try:
            db.session.execute(insert(Student.__table__).values(studentID=existing.userID, totalHours=0, points=0))
            existing.user_type = 'student'
            db.session.commit()
            return db.session.get(User, existing.userID)
        except Exception as e:
            db.session.rollback()
            print(f"Error converting existing user to student: {e}")
            return None
    newstudent = Student(username=username, password=password)
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
