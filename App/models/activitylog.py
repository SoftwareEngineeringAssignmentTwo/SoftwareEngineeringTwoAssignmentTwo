from App.database import db
from datetime import datetime
import uuid

class ActivityLog(db.Model):
    __table_args__ = {'extend_existing': True}
    logID = db.Column(db.String, primary_key=True)
    studentID = db.Column(db.String, db.ForeignKey('student.studentID'), nullable=False)
    hoursLogged = db.Column(db.Integer, nullable=False)
    dateLogged = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def __init__(self, *args, **kwargs):
        """Flexible constructor:
        - Can be called as ActivityLog(studentID, hoursLogged, description)
        - Or with full explicit fields: ActivityLog(logID, studentID, hoursLogged, dateLogged, status, description)
        """
        if len(args) == 3:
            # (studentID, hoursLogged, description)
            studentID, hoursLogged, description = args
            self.logID = kwargs.get('logID', str(uuid.uuid4()))
            self.studentID = studentID
            self.hoursLogged = hoursLogged
            self.dateLogged = kwargs.get('dateLogged', datetime.utcnow())
            self.status = kwargs.get('status', 'logged')
            self.description = description
        else:
            # Fallback to explicit kw args or full signature
            self.logID = kwargs.get('logID', args[0] if len(args) > 0 else str(uuid.uuid4()))
            self.studentID = kwargs.get('studentID', args[1] if len(args) > 1 else None)
            self.hoursLogged = kwargs.get('hoursLogged', args[2] if len(args) > 2 else 0)
            self.dateLogged = kwargs.get('dateLogged', args[3] if len(args) > 3 else datetime.utcnow())
            self.status = kwargs.get('status', args[4] if len(args) > 4 else 'logged')
            self.description = kwargs.get('description', args[5] if len(args) > 5 else '')
    
    @staticmethod
    def createLog(studentID: str, hours: int, description: str) -> 'ActivityLog':
        new_log = ActivityLog(
            logID=str(uuid.uuid4()),
            studentID=studentID,
            hoursLogged=hours,
            dateLogged=datetime.utcnow(),
            status="logged",
            description=description
        )
        db.session.add(new_log)
        db.session.commit()
        return new_log

    def to_json(self) -> dict:
        return {
            'logID': self.logID,
            'studentID': self.studentID,
            'hoursLogged': self.hoursLogged,
            'dateLogged': self.dateLogged.isoformat() if isinstance(self.dateLogged, datetime) else self.dateLogged,
            'status': self.status,
            'description': self.description
        }

    def updateStatus(self, newStatus: str) -> None:
        self.status = newStatus

    def getHoursLogged(self) -> int:
        return self.hoursLogged

    def getDescription(self) -> str:
        return self.description