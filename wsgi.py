import click # This is used to create CLI commands
import pytest # This is used to run tests
import sys # This is used to exit the program
import uuid # This is used to generate unique IDs for the users
from flask.cli import AppGroup

from App.database import get_migrate, db
from sqlalchemy import desc
from App.models import User
from App.main import create_app
from App.controllers import (create_user, get_all_users_json, get_all_users,initialize)
from App.models.user import Student, LeaderBoardEntry, Accolade, ActivityLog, Staff

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)


# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()

    # Check if users already exist before creating them
    if not User.query.filter_by(username='bob').first():
        bob = User(username='bob', password='bobpass')
        db.session.add(bob)
        print('Created user: bob')
    else:
        print('User bob already exists')

    if not User.query.filter_by(username='sally').first():
        sally = User(username='sally', password='sallypass')
        db.session.add(sally)
        print('Created user: sally')
    else:
        print('User sally already exists')

    if not User.query.filter_by(username='rob').first():
        rob = User(username='rob', password='robpass')
        db.session.add(rob)
        print('Created user: rob')
    else:
        print('User rob already exists')

    # Create staff accounts interactively
    print("\n--- Create Staff Accounts ---")
    while True:
        staff_username = input("Enter staff username (or 'exit' to quit): ")
        if staff_username == 'exit':
            break
        staff_password = input("Enter staff password: ")
        if not Staff.query.filter_by(username=staff_username).first():
            staff = Staff(username=staff_username, password=staff_password)
            db.session.add(staff)
            print(f'Created staff: {staff_username}')
        else:
            print(f'Staff {staff_username} already exists')

    # Create student accounts interactively
    print("\n--- Create Student Accounts ---")
    while True:
        student_username = input("Enter student username (or 'exit' to quit): ")
        if student_username == 'exit':
            break
        student_password = input("Enter student password: ")
        if not Student.query.filter_by(username=student_username).first():
            student = Student(username=student_username, password=student_password)
            db.session.add(student)
            print(f'Created student: {student_username}')
        else:
            print(f'Student {student_username} already exists')
    db.session.commit()
    print('database intialized')


'''
User Commands
'''


@app.cli.command("staff-log-hours", help="Staff log hours for a student")
@click.argument('staff_username', default='staff1')
@click.argument('student_username', default='student1')
@click.argument('hours', default='10')
@click.argument('activity', default='community service')
def staff_log_hours_command(staff_username, student_username, hours, activity):
    staff = Staff.query.filter_by(username=staff_username).first()
    student = Student.query.filter_by(username=student_username).first()
    if not staff:
        print(f'Staff {staff_username} not found!')
        return
    if not student:
        print(f'Student {student_username} not found!')
        return
    log = staff.logHoursForStudent(student.studentID, int(hours), activity)
    db.session.commit()
    print(
        f'Staff {staff_username} logged {hours} hours for student {student_username}'
    )
    print(f'Activity: {activity}')
    print(f'Log ID: {log.logID}')


@app.cli.command("request-confirmation",
                 help="Student request confirmation of hours")
@click.argument('student_username', default='student1')
@click.argument('activity_log_id')
def request_confirmation_command(student_username, activity_log_id):
    student = Student.query.filter_by(username=student_username).first()
    if not student:
        print(f'Student {student_username} not found!')
        return
    activity_log = ActivityLog.query.filter_by(
        logID=activity_log_id, studentID=student.studentID).first()
    if not activity_log:
        print(
            f'Activity log {activity_log_id} not found for student {student_username}!'
        )
        return
    student.requestConfirmationOfHours(activity_log_id)
    print(
        f'Student {student_username} requested confirmation for activity log {activity_log_id}'
    )
    print('Status changed to: pending')


@app.cli.command("view-leaderboard",
                 help="View student leaderboard ranked by confirmed hours")
def view_leaderboard_command():
    # Get all students with confirmed hours
    students = Student.query.all()
    leaderboard_data = []

    for student in students:
        confirmed_logs = ActivityLog.query.filter_by(
            studentID=student.studentID, status='confirmed').all()
        total_confirmed_hours = sum(log.hoursLogged for log in confirmed_logs)
        accolades_count = len(student.viewAccolades())
        leaderboard_data.append({
            'username': student.username,
            'studentID': student.studentID,
            'total_hours': total_confirmed_hours,
            'accolades': accolades_count
        })

    # Sort by total hours descending
    leaderboard_data.sort(key=lambda x: x['total_hours'], reverse=True)

    print("Student Leaderboard (Ranked by Confirmed Community Service Hours):")
    print("=" * 70)
    for rank, entry in enumerate(leaderboard_data, 1):
        print(
            f"{rank}. {entry['username']} - {entry['total_hours']} hours - {entry['accolades']} accolades"
        )

    if not leaderboard_data:
        print("No students found with confirmed hours.")


@app.cli.command("view-accolades", help="Student view their earned accolades")
@click.argument('student_username', default='student1')
def view_accolades_command(student_username):
    student = Student.query.filter_by(username=student_username).first()
    if not student:
        print(f'Student {student_username} not found!')
        return

    # Get confirmed hours for milestone calculation
    confirmed_logs = ActivityLog.query.filter_by(studentID=student.studentID,status='confirmed').all()
    total_confirmed_hours = sum(log.hoursLogged for log in confirmed_logs)

    # Update student's totalHours
    student.totalHours = total_confirmed_hours
    db.session.commit()

    print(f"Accolades for {student_username}:")
    print(f"Total confirmed community service hours: {total_confirmed_hours}")
    print("=" * 50)

    # Accolades are automatically created when hours are confirmed by staff

    # Now display the actual accolade records from the database
    student_accolades = student.viewAccolades()

    if student_accolades:
        for i, accolade in enumerate(student_accolades, 1):
            print(f"{i}. {accolade.name}")
    else:
        print("No accolades earned yet. Keep volunteering!")
        print("Next milestone: 10 hours")


@app.cli.command("staff-confirm-hours", help="Staff confirm student hours")
@click.argument('staff_username', default='staff1')
@click.argument('activity_log_id')
def staff_confirm_hours_command(staff_username, activity_log_id):
    staff = Staff.query.filter_by(username=staff_username).first()
    if not staff:
        print(f'Staff {staff_username} not found!')
        return

    activity_log = ActivityLog.query.filter_by(logID=activity_log_id).first()
    if not activity_log:
        print(f'Activity log {activity_log_id} not found!')
        return

    if activity_log.status == 'confirmed':
        print(f'Activity log {activity_log_id} is already confirmed!')
        return

    staff.confirmHours(activity_log_id)

    # Update student's total hours
    student = Student.query.filter_by(studentID=activity_log.studentID).first()
    if student:
        confirmed_logs = ActivityLog.query.filter_by(
            studentID=student.studentID, status='confirmed').all()
        student.totalHours = sum(log.hoursLogged for log in confirmed_logs)
        db.session.commit()

    print(f'Staff {staff_username} confirmed activity log {activity_log_id}')
    print(f'Hours confirmed: {activity_log.hoursLogged}')
    print(f'Activity: {activity_log.getDescription()}')


@app.cli.command("view-activity-log", help="View details of a specific activity log")
@click.argument('activity_log_id')
def view_activity_log_command(activity_log_id):
    activity_log = ActivityLog.query.filter_by(logID=activity_log_id).first()
    if not activity_log:
        print(f'Activity log {activity_log_id} not found!')
        return
    
    student = Student.query.filter_by(studentID=activity_log.studentID).first()
    print("Activity Log Details:")
    print(f"ID: {activity_log.logID}")
    print(f"Student: {student.username if student else 'Unknown'}")
    print(f"Hours: {activity_log.getHoursLogged()}")
    print(f"Description: {activity_log.getDescription()}")
    print(f"Status: {activity_log.status}")
    print(f"Date: {activity_log.dateLogged}")

@app.cli.command("staff-reject-hours", help="Staff reject student hours")
@click.argument('staff_username', default='staff1')
@click.argument('activity_log_id')
def staff_reject_hours_command(staff_username, activity_log_id):
    staff = Staff.query.filter_by(username=staff_username).first()
    if not staff:
        print(f'Staff {staff_username} not found!')
        return

    activity_log = ActivityLog.query.filter_by(logID=activity_log_id).first()
    if not activity_log:
        print(f'Activity log {activity_log_id} not found!')
        return

    if activity_log.status != 'pending':
        print(f'Activity log {activity_log_id} is not in pending status! Current status: {activity_log.status}')
        return

    staff.rejectHours(activity_log_id)

    print(f'Staff {staff_username} rejected activity log {activity_log_id}')
    print(f'Hours rejected: {activity_log.hoursLogged}')
    print(f'Activity: {activity_log.getDescription()}')
    print('Status changed to: rejected')

@app.cli.command("update-leaderboard",
                 help="Update leaderboard entries for all students")
def update_leaderboard_command():
    students = Student.query.all()

    for student in students:
        # Calculate confirmed hours and accolades
        confirmed_logs = ActivityLog.query.filter_by(
            studentID=student.studentID, status='confirmed').all()
        total_confirmed_hours = sum(log.hoursLogged for log in confirmed_logs)
        total_accolades = len(student.viewAccolades())

        # Update student's totalHours
        student.totalHours = total_confirmed_hours

        # Check if leaderboard entry exists
        existing_entry = LeaderBoardEntry.query.filter_by(
            studentID=student.studentID).first()

        if existing_entry:
            existing_entry.updateEntry(student)
        else:
            # Create new leaderboard entry
            new_entry = LeaderBoardEntry(
                entryID=str(uuid.uuid4()),
                studentID=student.studentID,
                rank=0,  # Will be calculated later
                totalHours=total_confirmed_hours,
                totalAccolades=total_accolades)
            db.session.add(new_entry)

    # Calculate ranks
    entries = LeaderBoardEntry.query.order_by(desc(
        LeaderBoardEntry.totalHours)).all()

    for rank, entry in enumerate(entries, 1):
        entry.rank = rank

    db.session.commit()
    print("Leaderboard updated successfully!")


# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands')


# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')


# this command will be : flask user create bob bobpass


@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())


app.cli.add_command(user_cli)  # add the group to the cli
'''
Test Commands
'''

test = AppGroup('test', help='Testing commands')


@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))


app.cli.add_command(test)
