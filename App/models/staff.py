from App.database import db
from App.database import db
from App.models.user import User
from datetime import datetime
import uuid
from App.models import Student, ActivityLog, Accolade, LeaderBoardEntry

class Staff(User):
    __tablename__ = 'staff'
    __table_args__ = {'extend_existing': True}
    staffID = db.Column(db.String, db.ForeignKey('user.userID'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'staff'
    }

    def __init__(self, username, password):
        super().__init__(username, password)
        self.staffID = self.userID

    @staticmethod
    def logHoursForStudent(studentID: str, hours: int, activity: str) -> 'ActivityLog':
        """Staff can log hours for a student. Made static so tests can call it directly via Staff.logHoursForStudent(...)."""
        new_log = ActivityLog.createLog(studentID, hours, activity)
        return new_log

    def confirmHours(self, activityLogID: str) -> None:
        activity_log = ActivityLog.query.filter_by(logID=activityLogID).first()
        if activity_log and activity_log.status == "pending":
            activity_log.status = "confirmed"
            # Update student's total hours when confirmed
            student = Student.query.filter_by(studentID=activity_log.studentID).first()
            if student:
                student.totalHours += activity_log.hoursLogged
                # Check for accolades based on milestones
                milestones = [10, 25, 50, 100]
                for milestone in milestones:
                    if student.totalHours >= milestone:
                        # Check if accolade already exists for this student and milestone
                        existing_accolade = Accolade.query.filter_by(
                            studentID=student.studentID, 
                            milestoneHours=milestone
                        ).first()
                        if not existing_accolade:
                            # Create and award the accolade
                            accolade = Accolade(
                                accoladeID=str(uuid.uuid4()),
                                studentID=student.studentID,
                                name=f"{milestone} Hour Milestone",
                                milestoneHours=milestone,
                                dateAwarded=datetime.utcnow()
                            )
                            db.session.add(accolade)
                # After awarding accolades and updating hours, ensure leaderboard entry is updated/created
                try:
                    LeaderBoardEntry.updateEntry(student)
                except Exception:
                    # Ignore errors here; leaderboard is non-critical for the flow
                    pass
            db.session.commit()

    def rejectHours(self, activityLogID: str) -> None:
        activity_log = ActivityLog.query.filter_by(logID=activityLogID).first()
        if activity_log and activity_log.status == "pending":
            activity_log.status = "rejected"
            db.session.commit()

    def viewLeaderboard(self) -> list:
        return LeaderBoardEntry.query.all()