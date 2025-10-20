import click # This is used to create CLI commands
import pytest # This is used to run tests
import sys # This is used to exit the program
import uuid # This is used to generate unique IDs for the users
from flask.cli import AppGroup

from App.database import get_migrate, db
from App.models import User
from App.main import create_app
from App.controllers import (
    create_user,
    get_all_users_json,
    get_all_users,
    initialize,
    # admin controllers
    initialize_full,
    staff_log_hours,
    request_confirmation,
    view_leaderboard,
    view_accolades,
    staff_confirm_hours,
    staff_reject_hours,
    update_leaderboard
)
from App.models.user import Student, LeaderBoardEntry, Accolade, ActivityLog, Staff

# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)


# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    created = initialize_full()
    if created:
        print('Created users: ' + ', '.join(created))
        print('Database Initialized')
    else:
        print('No new users created or already existed')


'''
User Commands
'''


@app.cli.command("staff-log-hours", help="Staff log hours for a student")
@click.argument('staff_username', default='staff1')
@click.argument('student_username', default='student1')
@click.argument('hours', default='10')
@click.argument('activity', default='community service')
def staff_log_hours_command(staff_username, student_username, hours, activity):
    log = staff_log_hours(staff_username, student_username, hours, activity)
    if not log:
        print('Staff or student not found')
        return
    print(f'Staff {staff_username} logged {hours} hours for student {student_username}')
    print(f'Activity: {activity}')
    print(f'Log ID: {log.logID}')


@app.cli.command("request-confirmation",
                 help="Student request confirmation of hours")
@click.argument('student_username', default='student1')
@click.argument('activity_log_id')
def request_confirmation_command(student_username, activity_log_id):
    activity_log = request_confirmation(student_username, activity_log_id)
    if not activity_log:
        print('Student or activity log not found')
        return
    print(f'Student {student_username} requested confirmation for activity log {activity_log_id}')
    print('Status changed to: pending')


@app.cli.command("view-leaderboard",
                 help="View student leaderboard ranked by confirmed hours")
def view_leaderboard_command():
    leaderboard_data = view_leaderboard()
    print("Student Leaderboard (Ranked by Confirmed Community Service Hours):")
    print("=" * 70)
    for rank, entry in enumerate(leaderboard_data, 1):
        print(f"{rank}. {entry['username']} - {entry['total_hours']} hours - {entry['accolades']} accolades")
    if not leaderboard_data:
        print("No students found with confirmed hours.")


@app.cli.command("view-accolades", help="Student view their earned accolades")
@click.argument('student_username', default='student1')
def view_accolades_command(student_username):
    result = view_accolades(student_username)
    if not result:
        print(f'Student {student_username} not found!')
        return
    print(f"Accolades for {student_username}:")
    print(f"Total confirmed community service hours: {result['total_hours']}")
    print("=" * 50)
    if result['accolades']:
        for i, name in enumerate(result['accolades'], 1):
            print(f"{i}. {name}")
    else:
        print("No accolades earned yet. Keep volunteering!")
        print("Next milestone: 10 hours")


@app.cli.command("staff-confirm-hours", help="Staff confirm student hours")
@click.argument('staff_username', default='staff1')
@click.argument('activity_log_id')
def staff_confirm_hours_command(staff_username, activity_log_id):
    activity_log = staff_confirm_hours(staff_username, activity_log_id)
    if not activity_log:
        print('Staff or activity log not found')
        return
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
    activity_log = staff_reject_hours(staff_username, activity_log_id)
    if not activity_log:
        print('Staff or activity log not found')
        return
    if activity_log.status != 'rejected':
        print(f'Activity log {activity_log_id} rejection failed or status not pending. Current status: {activity_log.status}')
        return
    print(f'Staff {staff_username} rejected activity log {activity_log_id}')
    print(f'Hours rejected: {activity_log.hoursLogged}')
    print(f'Activity: {activity_log.getDescription()}')
    print('Status changed to: rejected')

@app.cli.command("update-leaderboard",
                 help="Update leaderboard entries for all students")
def update_leaderboard_command():
    count = update_leaderboard()
    print(f"Leaderboard updated successfully! {count} entries updated")


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
