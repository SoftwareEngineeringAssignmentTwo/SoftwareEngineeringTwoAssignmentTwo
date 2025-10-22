import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, ActivityLog, Accolade, LeaderBoardEntry, Staff
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

class UsersIntegrationTests(unittest.TestCase):

    def test_student_workflow(self):
        student = create_user("alice", "alicepass", user_type="student")
        staff = create_user("admin", "adminpass", user_type="staff")
        log = Staff.logHoursForStudent(student.studentID, 5, "Volunteering")
        self.assertEqual(log.status, "logged")
        # Simulate student requesting confirmation
        log.status = "pending"
        db.session.commit()
        Staff.confirmHours(self, log.logID)
        updated_log = ActivityLog.query.filter_by(logID=log.logID).first()
        self.assertEqual(updated_log.status, "confirmed")
   
    def test_accolade_awarding(self):
        student = create_user("charlie", "charliepass", user_type="student")
        staff = create_user("admin2", "adminpass2", user_type="staff")
        # Log hours to reach milestone
        log = Staff.logHoursForStudent(student.studentID, 50, "Community Service")
        log.status = "pending"
        db.session.commit()
        Staff.confirmHours(self, log.logID)
        # Check if accolade awarded
        accolade = Accolade.query.filter_by(studentID=student.studentID, milestoneHours=50).first()
        self.assertIsNotNone(accolade)
    
    def test_leaderboard_ranking(self):
        student1 = create_user("dave", "davepass", user_type="student")
        staff = create_user("admin3", "adminpass3", user_type="staff")
        log1 = Staff.logHoursForStudent(student1.studentID, 30, "Volunteering")
        log2 = Staff.logHoursForStudent(student1.studentID, 20, "Community Service")
        log1.status = "pending"
        log2.status = "pending"
        db.session.commit()
        Staff.confirmHours(self, log1.logID)
        Staff.confirmHours(self, log2.logID)
        # Check leaderboard ranking
        entry = LeaderBoardEntry.query.filter_by(studentID=student1.studentID).first()
        self.assertEqual(entry.totalHours, 50)

    def test_staff_authentication(self):
        staff = create_user("eve", "evepass", user_type="staff")
        token = login("eve", "evepass")
        self.assertIsNotNone(token)
    
    def test_hour_rejection_workflow(self):
        student = create_user("frank", "frankpass", user_type="student")
        staff = create_user("admin4", "adminpass4", user_type="staff")
        log = Staff.logHoursForStudent(student.studentID, 10, "Event Help")
        log.status = "pending"
        db.session.commit()
        # Simulate staff rejecting hours
        activity_log = ActivityLog.query.filter_by(logID=log.logID).first()
        if activity_log and activity_log.status == "pending":
            activity_log.status = "rejected"
            db.session.commit()
        



    







        

