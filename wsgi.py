import click
import pytest
import sys
from flask.cli import AppGroup

from App.database import get_migrate, db
from sqlalchemy import desc
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

    # Create students
    if not Student.query.filter_by(username='student1').first():
        student1 = Student(username='student1', password='student1pass')
        db.session.add(student1)
        print('Created student: student1')
    else:
        print('Student student1 already exists')
        student1 = Student.query.filter_by(username='student1').first()
        
    if not Student.query.filter_by(username='student2').first():
        student2 = Student(username='student2', password='student2pass')
        db.session.add(student2)
        print('Created student: student2')
    else:
        print('Student student2 already exists')
        student2 = Student.query.filter_by(username='student2').first()

    # Create staff
    if not Staff.query.filter_by(username='staff1').first():
        staff1 = Staff(username='staff1', password='staff1pass')
        db.session.add(staff1)
        print('Created staff: staff1')
    else:
        print('Staff staff1 already exists')
        
    if not Staff.query.filter_by(username='staff2').first():
        staff2 = Staff(username='staff2', password='staff2pass')
        db.session.add(staff2)
        print('Created staff: staff2')
    else:
        print('Staff staff2 already exists')
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
    print(f'Staff {staff_username} logged {hours} hours for student {student_username}')
    print(f'Activity: {activity}')
    print(f'Log ID: {log.logID}')

@app.cli.command("request-confirmation", help="Student request confirmation of hours")
@click.argument('student_username', default='student1')
@click.argument('activity_log_id')
def request_confirmation_command(student_username, activity_log_id):
    student = Student.query.filter_by(username=student_username).first()
    if not student:
        print(f'Student {student_username} not found!')
        return
    activity_log = ActivityLog.query.filter_by(logID=activity_log_id, studentID=student.studentID).first()
    if not activity_log:
        print(f'Activity log {activity_log_id} not found for student {student_username}!')
        return
    student.requestConfirmationOfHours(activity_log_id)
    print(f'Student {student_username} requested confirmation for activity log {activity_log_id}')
    print('Status changed to: pending')

@app.cli.command("view-leaderboard", help="View student leaderboard ranked by confirmed hours")
def view_leaderboard_command():
    # Get all students with confirmed hours
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
    
    # Sort by total hours descending
    leaderboard_data.sort(key=lambda x: x['total_hours'], reverse=True)
    
    print("Student Leaderboard (Ranked by Confirmed Community Service Hours):")
    print("=" * 70)
    for rank, entry in enumerate(leaderboard_data, 1):
        print(f"{rank}. {entry['username']} - {entry['total_hours']} hours - {entry['accolades']} accolades")
    
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
    confirmed_logs = ActivityLog.query.filter_by(studentID=student.studentID, status='confirmed').all()
    total_confirmed_hours = sum(log.hoursLogged for log in confirmed_logs)
    
    print(f"Accolades for {student_username}:")
    print(f"Total confirmed community service hours: {total_confirmed_hours}")
    print("=" * 50)
    
    # Check for milestones and create/award accolades if not already awarded
    milestones = [10, 25, 50, 100, 200, 300]
    
    for milestone in milestones:
        if total_confirmed_hours >= milestone:
            milestone_name = f"{milestone} Hour Milestone"
            
            # Check if student already has this accolade
            existing_accolade = Accolade.query.filter_by(
                studentID=student.studentID, 
                name=milestone_name
            ).first()
            
            if not existing_accolade:
                # Create the accolade and award it to the student
                new_accolade = Accolade.createAccolade(milestone_name, milestone)
                Accolade.awardAccolade(student.studentID, new_accolade.accoladeID)
    
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
    print(f'Staff {staff_username} confirmed activity log {activity_log_id}')
    print(f'Hours confirmed: {activity_log.hoursLogged}')
    print(f'Activity: {activity_log.description}')


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