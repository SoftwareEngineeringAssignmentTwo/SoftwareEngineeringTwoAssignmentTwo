from App.database import db
from datetime import datetime
import uuid

class Accolade(db.Model):
    __table_args__ = {'extend_existing': True}
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