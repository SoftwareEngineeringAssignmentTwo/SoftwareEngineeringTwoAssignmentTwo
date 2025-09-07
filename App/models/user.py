from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    userID = db.Column(db.Integer, primary_key=True)
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
        # Logic for logging out the user
        pass

    def changePassword(oldPass: str, newPass: str) -> bool:
        if self.check_password(oldPass):
            self.set_password(newPass)
            return True
        return False
    
class Student(User):
    studentID = db.Column(db.String, db.ForeignKey('user.userID'), primary_key=True)
    totalHours = db.Column(db.Integer, nullable=False, default=0)
    points = db.Column(db.Integer, nullable=False, default=0)

    def requestConfirmationOfHours(activityLogID: str) -> None:
        # Logic for requesting confirmation of hours
        pass

    def viewLeaderboard() -> list:
        # Logic for viewing the leaderboard
        pass

    def viewAccolades() -> list:
        # Logic for viewing accolades
        pass

    def logHours(hours: int, description: str) -> ActivityLog:
        # Logic for logging hours
        pass

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
        # Logic for creating an accolade
        pass

    @staticmethod
    def awardAccolade(studentID: str, accoladeID: str) -> None:
        # Logic for awarding an accolade
        pass

class Staff(User):
    staffID = db.Column(db.String, primary_key=True)

    def confirmHours(activityLogID: str) -> None:
        # Logic for confirming hours
        pass

    def viewLeaderboard() -> list:
        # Logic for viewing the leaderboard
        pass

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
        # Logic for creating a new activity log
        pass

    def updateStatus(newStatus: str) -> None:
        self.status = newStatus

    def getHoursLogged() -> int:
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

    def updateEntry(student: Student) -> None:
        # Logic for updating the leaderboard entry
        pass

    def getRank() -> int:
        return self.rank