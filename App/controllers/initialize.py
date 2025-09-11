from .user import create_user
from App.database import db


def initialize():
    # Ensure all models are imported before create_all
    from App.models import User, Student, Staff, ActivityLog, Accolade, LeaderBoardEntry
    db.drop_all()
    db.create_all()
    create_user('bob', 'bobpass')
