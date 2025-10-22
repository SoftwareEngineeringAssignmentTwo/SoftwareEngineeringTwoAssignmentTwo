from functools import wraps
from flask import jsonify
from flask_jwt_extended import create_access_token, current_user, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request

from App.models import User
from App.database import db

def login(username, password, user_type=None):
  result = db.session.execute(db.select(User).filter_by(username=username))
  user = result.scalar_one_or_none()
  if user and user.check_password(password):
    if user_type is None or user.user_type == user_type:
        # Store ONLY the user id as a string in JWT 'sub'
        return create_access_token(identity=str(user.userID))
  return None

def login_required(required_class):
  def decorator(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
      #Check if current_user is an instance of the required class
      if not isinstance(current_user, required_class):
        return jsonify({
          'error': 'Unauthorized access',
          'message': f'User must be an instance of {required_class.__name__} to access this resource.'
        }), 401
      return f(*args, **kwargs)
    return decorated_function
  return decorator 

def setup_jwt(app):
  jwt = JWTManager(app)

  # Always store a string user id in the JWT identity (sub),
  # whether a User object or a raw id is passed.
  @jwt.user_identity_loader
  def user_identity_lookup(identity):
    user_id = getattr(identity, "id", identity)
    return str(user_id) if user_id is not None else None

  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    # Use string userID for lookup
    return db.session.get(User, identity)

  return jwt


# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          identity = get_jwt_identity()
          current_user = db.session.get(User, identity) if identity is not None else None
          is_authenticated = current_user is not None
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)