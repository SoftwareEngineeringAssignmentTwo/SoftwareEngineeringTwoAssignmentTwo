import click
import pytest
import sys
from flask.cli import AppGroup

from App.database import get_migrate, db
from App.models import User
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
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

    # Create a student
    student = Student(username='student1', password='student1pass')

    # Create a leaderboard entry for the student
    leaderboard_entry = LeaderBoardEntry(entryID='1', studentID=student.studentID, rank=1, totalHours=100, totalAccolades=5)
    db.session.add(student)
    db.session.add(leaderboard_entry)

    # Allocades
    accolade1 = Accolade.createAccolade('Bronze', 100)
    accolade2 = Accolade.createAccolade('Silver', 200)
    accolade3 = Accolade.createAccolade('Gold', 300)
    db.session.add_all([accolade1, accolade2, accolade3])

    # ActivityLogs
    log1 = ActivityLog.createLog(student.studentID, 10, 'Completed assignment')
    log2 = ActivityLog.createLog(student.studentID, 20, 'Attended workshop')
    db.session.add_all([log1, log2])

    # Staff
    staff = Staff(username='staff1', password='staff1pass')
    db.session.add(staff)
    db.session.commit()
    print('database intialized')

'''
User Commands
'''

@app.cli.command("log_hours", help="Log hours for a student")
@click.argument("student_id")
@click.argument("hours")
@click.argument("activity")
def log_hours_command(student_id, hours, activity):
    student = Student.query.filter_by(studentID=student_id).first()
    if student:
        log = student.logHours(int(hours), activity)
        print(f'Logged {hours} hours for {student_id} with log ID {log.logID}')

@app.cli.command("request_confirmation", help="Request confirmation of hours")
@click.argument("student_id")
@click.argument("activity_log_id")
def request_confirmation_command(student_id, activity_log_id):
    student = Student.query.filter_by(studentID=student_id).first()
    if student:
        student.requestConfirmationOfHours(activity_log_id)

@app.cli.command("view_leaderboard", help="View student leaderboard")
def view_leaderboard_command():
    leaderboard = LeaderBoardEntry.query.order_by(LeaderBoardEntry.totalHours.desc()).all()
    for entry in leaderboard:
        print(f'Student ID: {entry.studentID}, Total Hours: {entry.totalHours}, Total Accolades: {entry.totalAccolades}, Rank: {entry.rank}')

@app.cli.command("view_accolades", help="View student accolades")
@click.argument("student_id")
def view_accolades_command(student_id):
    student = Student.query.filter_by(studentID=student_id).first()
    if student:
        accolades = student.viewAccolades()
        for accolade in accolades:
            print(f'Accolade ID: {accolade.accoladeID}, Date Awarded: {accolade.dateAwarded}')
    pass

@app.cli.command("view_leaderboard", help="View student leaderboard")
def view_leaderboard_command():
    leaderboard = LeaderBoardEntry.query.order_by(LeaderBoardEntry.totalHours.desc()).all()
    for entry in leaderboard:
        print(f'Student ID: {entry.studentID}, Total Hours: {entry.totalHours}, Total Accolades: {entry.totalAccolades}, Rank: {entry.rank}')


@app.cli.command("view_accolades", help="View student accolades")
@click.argument("student_id")
def view_accolades_command(student_id):
    student = Student.query.filter_by(studentID=student_id).first()
    if student:
        accolades = student.viewAccolades()
        for accolade in accolades:
            print(f'Accolade ID: {accolade.accoladeID}, Date Awarded: {accolade.dateAwarded}')
    pass

@app.cli.command("view_leaderboard", help="View student leaderboard")
def view_leaderboard_command():
    leaderboard = LeaderBoardEntry.query.order_by(LeaderBoardEntry.totalHours.desc()).all()
    for entry in leaderboard:
        print(f'Student ID: {entry.studentID}, Total Hours: {entry.totalHours}, Total Accolades: {entry.totalAccolades}, Rank: {entry.rank}')
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

app.cli.add_command(user_cli) # add the group to the cli

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