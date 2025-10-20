from App.models import Student, LeaderBoardEntry, Accolade, ActivityLog, Staff, User
from App.database import db
from .initialize import initialize as initialize_schema
from .user import create_user
import uuid
from sqlalchemy import desc

def initialize_full(interactive=False):
    """Initialize schema and create default users. If interactive is True,
    controllers will not prompt; interactive prompting should be handled by CLI."""
    # Reset schema
    initialize_schema()

    # Create default users
    created = []
    for u, p in [('bob','bobpass'), ('sally','sallypass'), ('rob','robpass')]:
        if not db.session.execute(db.select(User).filter_by(username=u)).scalar_one_or_none():
            create_user(u, p)
            created.append(u)

    return created

def staff_log_hours(staff_username, student_username, hours, activity):
    staff = Staff.query.filter_by(username=staff_username).first()
    student = Student.query.filter_by(username=student_username).first()
    if not staff or not student:
        return None
    log = staff.logHoursForStudent(student.studentID, int(hours), activity)
    db.session.commit()
    return log

def request_confirmation(student_username, activity_log_id):
    student = Student.query.filter_by(username=student_username).first()
    if not student:
        return None
    activity_log = ActivityLog.query.filter_by(logID=activity_log_id, studentID=student.studentID).first()
    if not activity_log:
        return None
    student.requestConfirmationOfHours(activity_log_id)
    db.session.commit()
    return activity_log

def view_leaderboard():
    students = Student.query.all()
    leaderboard_data = []
    for student in students:
        confirmed_logs = ActivityLog.query.filter_by(studentID=student.studentID, status='confirmed').all()
        total_confirmed_hours = sum(log.hoursLogged for log in confirmed_logs)
        accolades_count = len(student.viewAccolades())
        leaderboard_data.append({
            'username': student.username,
            'studentID': student.studentID,
            'total_hours': total_confirmed_hours,
            'accolades': accolades_count
        })
    leaderboard_data.sort(key=lambda x: x['total_hours'], reverse=True)
    return leaderboard_data

def view_accolades(student_username):
    student = Student.query.filter_by(username=student_username).first()
    if not student:
        return None
    confirmed_logs = ActivityLog.query.filter_by(studentID=student.studentID, status='confirmed').all()
    total_confirmed_hours = sum(log.hoursLogged for log in confirmed_logs)
    student.totalHours = total_confirmed_hours
    db.session.commit()
    student_accolades = student.viewAccolades()
    return {'total_hours': total_confirmed_hours, 'accolades': [a.name for a in student_accolades]}

def staff_confirm_hours(staff_username, activity_log_id):
    staff = Staff.query.filter_by(username=staff_username).first()
    if not staff:
        return None
    activity_log = ActivityLog.query.filter_by(logID=activity_log_id).first()
    if not activity_log:
        return None
    if activity_log.status == 'confirmed':
        return activity_log
    staff.confirmHours(activity_log_id)
    # Update student's total hours
    student = Student.query.filter_by(studentID=activity_log.studentID).first()
    if student:
        confirmed_logs = ActivityLog.query.filter_by(studentID=student.studentID, status='confirmed').all()
        student.totalHours = sum(log.hoursLogged for log in confirmed_logs)
        db.session.commit()
    return activity_log

def staff_reject_hours(staff_username, activity_log_id):
    staff = Staff.query.filter_by(username=staff_username).first()
    if not staff:
        return None
    activity_log = ActivityLog.query.filter_by(logID=activity_log_id).first()
    if not activity_log:
        return None
    if activity_log.status != 'pending':
        return activity_log
    staff.rejectHours(activity_log_id)
    db.session.commit()
    return activity_log

def update_leaderboard():
    students = Student.query.all()
    for student in students:
        confirmed_logs = ActivityLog.query.filter_by(studentID=student.studentID, status='confirmed').all()
        total_confirmed_hours = sum(log.hoursLogged for log in confirmed_logs)
        total_accolades = len(student.viewAccolades())
        student.totalHours = total_confirmed_hours
        existing_entry = LeaderBoardEntry.query.filter_by(studentID=student.studentID).first()
        if existing_entry:
            existing_entry.updateEntry(student)
        else:
            new_entry = LeaderBoardEntry(
                entryID=str(uuid.uuid4()),
                studentID=student.studentID,
                rank=0,
                totalHours=total_confirmed_hours,
                totalAccolades=total_accolades
            )
            db.session.add(new_entry)
    entries = LeaderBoardEntry.query.order_by(desc(LeaderBoardEntry.totalHours)).all()
    for rank, entry in enumerate(entries, 1):
        entry.rank = rank
    db.session.commit()
    return len(entries)
