from App.database import db
from App.models.user import User

"""
Deliberately avoid importing other model classes at module level to prevent
circular import problems. Methods will import required models lazily.
"""

class Student(User):
    __tablename__ = 'student'
    __table_args__ = {'extend_existing': True}
    studentID = db.Column(db.String, db.ForeignKey('user.userID'), primary_key=True)
    totalHours = db.Column(db.Integer, nullable=False, default=0)
    points = db.Column(db.Integer, nullable=False, default=0)
    
    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }

    def __init__(self, username, password):
        super().__init__(username, password)
        self.studentID = self.userID

    def requestConfirmationOfHours(self, activityLogID: str) -> None:
        from App.models.activitylog import ActivityLog
        activity_log = ActivityLog.query.filter_by(logID=activityLogID, studentID=self.studentID).first()
        if activity_log and activity_log.status == "logged":
            activity_log.status = "pending"
            db.session.commit()

    def viewLeaderboard(self) -> list:
        from App.models.leaderboardentry import LeaderBoardEntry
        return LeaderBoardEntry.query.filter_by(studentID=self.studentID).all()

    def viewAccolades(self) -> list:
        from App.models.accolade import Accolade
        return Accolade.query.filter_by(studentID=self.studentID).all()