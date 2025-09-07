from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from datetime import datetime
import uuid

class User(db.Model):
    userID = db.Column(db.String, primary_key=True)
    username =  db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def login(username: str, password: str) -> bool:
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return True
        return False

    def logout() -> None:
        pass

    def changePassword(self, oldPass: str, newPass: str) -> bool:
        if self.check_password(oldPass):
            self.set_password(newPass)
            return True
        return False
    
class Student(User):
    studentID = db.Column(db.String, db.ForeignKey('user.userID'), primary_key=True)
    totalHours = db.Column(db.Integer, nullable=False, default=0)
    points = db.Column(db.Integer, nullable=False, default=0)

    def requestConfirmationOfHours(self, activityLogID: str) -> None:
        activity_log = ActivityLog.query.filter_by(logID=activityLogID, studentID=self.studentID).first()
        if activity_log:
            activity_log.status = "pending"
            db.session.commit()

    def viewLeaderboard(self) -> list:
        return LeaderBoardEntry.query.filter_by(studentID=self.studentID).all()

    def viewAccolades(self) -> list:
        return Accolade.query.filter_by(studentID=self.studentID).all()

    def logHours(self, hours: int, description: str) -> 'ActivityLog':
        new_log = ActivityLog.createLog(self.studentID, hours, description)
        db.session.add(new_log)
        db.session.commit()
        return new_log

class Accolade(db.Model):
    accoladeID = db.Column(db.String, primary_key=True)
    studentID = db.Column(db.String, db.ForeignKey('student.studentID'), nullable=False)
    name = db.Column(db.String, nullable=False)
    milestoneHours = db.Column(db.Integer, nullable=False)
    dateAwarded = db.Column(db.Date, nullable=False)

    def __init__(self, accoladeID, studentID, name, milestoneHours, dateAwarded):
        self.accoladeID = accoladeID
        self.studentID = studentID
        self.name = name
        self.milestoneHours = milestoneHours
        self.dateAwarded = dateAwarded

    @staticmethod
    def createAccolade(name: str, milestone: int) -> 'Accolade':
        new_accolade = Accolade(
            accoladeID=str(uuid.uuid4()),
            studentID=None,
            name=name,
            milestoneHours=milestone,
            dateAwarded=datetime.utcnow()
        )
        db.session.add(new_accolade)
        db.session.commit()
        return new_accolade

    @staticmethod
    def awardAccolade(studentID: str, accoladeID: str) -> None:
        accolade = Accolade.query.filter_by(accoladeID=accoladeID).first()
        if accolade:
            accolade.studentID = studentID
            db.session.commit()

class Staff(User):
    staffID = db.Column(db.String, db.ForeignKey('user.userID'), primary_key=True)

    def confirmHours(activityLogID: str) -> None:
        activity_log = ActivityLog.query.filter_by(logID=activityLogID).first()
        if activity_log:
            activity_log.status = "confirmed"
            db.session.commit()

    def viewLeaderboard() -> list:
        return LeaderBoardEntry.query.all()

class ActivityLog(db.Model):
    logID = db.Column(db.String, primary_key=True)
    studentID = db.Column(db.String, db.ForeignKey('student.studentID'), primary_key=True)
    hoursLogged = db.Column(db.Integer, nullable=False)
    dateLogged = db.Column(db.Date, nullable=False)
    status = db.Column(db.String, nullable=False)

    def __init__(self, logID, studentID, hoursLogged, dateLogged, status):
        self.logID = logID
        self.studentID = studentID
        self.hoursLogged = hoursLogged
        self.dateLogged = dateLogged
        self.status = status
    
    @staticmethod
    def createLog(studentID: str, hours: int, description: str) -> 'ActivityLog':
        new_log = ActivityLog(
            logID=str(uuid.uuid4()),
            studentID=studentID,
            hoursLogged=hours,
            dateLogged=datetime.utcnow(),
            status="pending"
        )
        db.session.add(new_log)
        db.session.commit()
        return new_log

    def updateStatus(self, newStatus: str) -> None:
        self.status = newStatus

    def getHoursLogged(self) -> int:
        return self.hoursLogged
    
class LeaderBoardEntry(db.Model):
    entryID = db.Column(db.String, primary_key=True)
    studentID = db.Column(db.String, db.ForeignKey('student.studentID'))
    rank = db.Column(db.Integer)
    totalHours = db.Column(db.Integer)
    totalAccolades = db.Column(db.Integer)

    def __init__(self, entryID, studentID, rank, totalHours, totalAccolades):
        self.entryID = entryID
        self.studentID = studentID
        self.rank = rank
        self.totalHours = totalHours
        self.totalAccolades = totalAccolades

    def updateEntry(self, student: Student) -> None:
        self.totalHours = student.totalHours
        self.totalAccolades = len(student.viewAccolades())
        db.session.commit()

    def getRank(self) -> int:
        return self.rank