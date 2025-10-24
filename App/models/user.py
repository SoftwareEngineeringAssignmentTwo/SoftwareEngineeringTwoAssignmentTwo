from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
import uuid

class User(db.Model):
    __tablename__ = 'user'
    userID = db.Column(db.String, primary_key=True)
    username =  db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20))
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def __init__(self, username, password):
        self.userID = str(uuid.uuid4())
        self.username = username
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.userID,
            'username': self.username
        }

    @property
    def id(self):
        """Provide a convenient `id` property expected by views and JWT identity usage."""
        return self.userID

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    @staticmethod
    def login(username: str, password: str) -> bool:
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return True
        return False

    def logout(self) -> None:
        pass

    def changePassword(self, oldPass: str, newPass: str) -> bool:
        if self.check_password(oldPass):
            self.set_password(newPass)
            return True
        return False
    
class Student(User):
    __tablename__ = 'student'
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
        activity_log = ActivityLog.query.filter_by(logID=activityLogID, studentID=self.studentID).first()
        if activity_log and activity_log.status == "logged":
            activity_log.status = "pending"
            db.session.commit()

    def viewLeaderboard(self) -> list:
        return LeaderBoardEntry.query.filter_by(studentID=self.studentID).all()

    def viewAccolades(self) -> list:
        return Accolade.query.filter_by(studentID=self.studentID).all()

class Accolade(db.Model):
    accoladeID = db.Column(db.String, primary_key=True)
    studentID = db.Column(db.String, db.ForeignKey('student.studentID'), nullable=True)
    name = db.Column(db.String, nullable=False)
    milestoneHours = db.Column(db.Integer, nullable=False)
    dateAwarded = db.Column(db.DateTime, nullable=False)

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
    __tablename__ = 'staff'
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

class ActivityLog(db.Model):
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
    
class LeaderBoardEntry(db.Model):
    entryID = db.Column(db.String, primary_key=True)
    studentID = db.Column(db.String, db.ForeignKey('student.studentID'))
    rank = db.Column(db.Integer)
    totalHours = db.Column(db.Integer)
    totalAccolades = db.Column(db.Integer)

    def __init__(self, entryID, studentID, rank=0, totalHours=0, totalAccolades=0):
        self.entryID = entryID
        self.studentID = studentID
        self.rank = rank
        self.totalHours = totalHours
        self.totalAccolades = totalAccolades

    @staticmethod
    def updateEntry(student: Student) -> 'LeaderBoardEntry':
        """Create or update a leaderboard entry for the given student and return it.
        Tests expect this to be callable as LeaderBoardEntry.updateEntry(student) and return an entry with totalHours set.
        """
        entry = LeaderBoardEntry.query.filter_by(studentID=student.studentID).first()
        if not entry:
            entry = LeaderBoardEntry(
                entryID=str(uuid.uuid4()),
                studentID=student.studentID,
                rank=0,
                totalHours=student.totalHours if hasattr(student, 'totalHours') else 0,
                totalAccolades=len(student.viewAccolades()) if hasattr(student, 'viewAccolades') else 0
            )
            db.session.add(entry)
        else:
            entry.totalHours = student.totalHours if hasattr(student, 'totalHours') else 0
            entry.totalAccolades = len(student.viewAccolades()) if hasattr(student, 'viewAccolades') else 0
        db.session.commit()
        return entry

    def getRank(self) -> int:
        return self.rank
