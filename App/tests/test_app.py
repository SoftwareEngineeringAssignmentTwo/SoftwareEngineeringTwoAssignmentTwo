import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user
)


LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):
    
    def test_create_accolade(self):
        accolade = Accolade("newbie", "10")
        assert accolade.name == "newbie"
        assert accolade.milestoneHours == "10"

    def test_change_password(self):
        newPassword = User.changePassword("12345", "54321")
        assert user.userPassword == "54321"

    def test_create_log(self):
        newActivity = ActivityLog("816000001","5","First Day")
        assert newActivity.studentID == "816000001"
        assert newActivity.hoursLogged == "5"
        assert newActivity.description == "First Day"

    def test_create_user(self):
        newUser = User("John Doe", "12345")
        assert newUser.userName == "John Doe"
        assert newUser.userPassword == "12345"



'''
    Integration Tests
'''

# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()

def test_authenticate():
    user = create_user("bob", "bobpass")
    assert login("bob", "bobpass") != None

class StudentStaffIntegrationTests(unittest.TestCase):
    #Student workflow tests
    def test_student_workflow(self):
        #Create staff and student
        staff = Staff("ada", "lovelace")
        student = Student("alan", "turing")
        db.session.add(staff)
        db.session.add(student)
        db.session.commit()

        #Staff logs hours for students
        activity_log = staff_log_hours ("ada", "alan", 15, "Flask-Dev")
        assert activity_log is not None
        assert activity_log.hoursLogged == 15
        assert activity_log.status == "logged"

        #Student Confirmation Request
        student.requestConfirmationOfHours(activity_log.logID)
        db.session.commit()

        #Verify student hours
        updated_log = ActivityLog.query.filter_by(logID=activity_log.logID).first()
        assert updated_log.status == "pending"

        #Staff confirms hours
        confirmed_log = staff_confirm_hours("ada", activity_log.logID)
        assert confirmed_log is not None
        assert confirmed_log.status == "confirmed"

        #Verify update to Student hours
        updated_student = Student.query.filter_by(username = "alan").first()
        assert updated_student.totalHours == 15

    #Accolade testing 😭
    def test_accolade_awarding(self):


    







        

