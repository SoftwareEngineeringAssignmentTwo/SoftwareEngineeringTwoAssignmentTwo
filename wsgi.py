import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
from App.models.user import Student, LeaderBoardEntry, Accolade, ActivityLog


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
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