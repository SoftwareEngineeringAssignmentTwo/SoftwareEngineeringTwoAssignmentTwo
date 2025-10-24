from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
import uuid

class User(db.Model):
    __tablename__ = 'user'
    userID = db.Column(db.String, primary_key=True)
    username =  db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20))
    
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

    def __init__(self, username, password):
        self.userID = str(uuid.uuid4())
        self.username = username
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.userID,
            'username': self.username
        }

    @property
    def id(self):
        """Provide a convenient `id` property expected by views and JWT identity usage."""
        return self.userID

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    @staticmethod
    def login(username: str, password: str) -> bool:
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return True
        return False

    def logout(self) -> None:
        pass

    def changePassword(self, oldPass: str, newPass: str) -> bool:
        if self.check_password(oldPass):
            self.set_password(newPass)
            return True
        return False
