from .user import User
from .activitylog import ActivityLog
from .accolade import Accolade
from .leaderboardentry import LeaderBoardEntry
from .student import Student
from .staff import Staff

# Handle circular dependencies
import App.models.student
import App.models.staff
import App.models.activitylog
import App.models.accolade
import App.models.leaderboardentry

# Make types available at module level
ActivityLog.Student = Student
Staff.Student = Student
Staff.ActivityLog = ActivityLog
Staff.Accolade = Accolade
Staff.LeaderBoardEntry = LeaderBoardEntry
Student.ActivityLog = ActivityLog
Student.LeaderBoardEntry = LeaderBoardEntry
Student.Accolade = Accolade
LeaderBoardEntry.Student = Student

__all__ = ['User', 'Student', 'Staff', 'Accolade', 'ActivityLog', 'LeaderBoardEntry']