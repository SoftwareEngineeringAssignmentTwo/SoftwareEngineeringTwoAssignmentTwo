rom App.database import db
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App.models.student import Student

class LeaderBoardEntry(db.Model):
    __table_args__ = {'extend_existing': True}
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
    def updateEntry(student: 'Student') -> 'LeaderBoardEntry':
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