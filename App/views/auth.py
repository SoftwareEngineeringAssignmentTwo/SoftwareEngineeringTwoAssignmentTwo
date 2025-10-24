from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies

from.index import index_views

from App.controllers import (
    login,
    create_user
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')




'''
Page/Action Routes
'''    

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
    

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'], data.get('user_type'))
    response = redirect(request.referrer)
    if not token:
        flash('Bad username or password given'), 401
    else:
        flash('Login Successful')
        set_access_cookies(response, token) 
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response

@auth_views.route('/api/staff', methods=['POST'])
def create_staff_api():
    try:
        data = request.json
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username or password'}), 400
        
        user = create_user(data['username'], data['password'], user_type='staff')
        if not user:
            return jsonify({'error': 'Failed to create staff user'}), 400
        
        return jsonify({'message': f'Staff {user.username} successfully created with id {user.id}'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_views.route('/api/students', methods=['POST'])
def create_student_api():
    try:
        data = request.json
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username or password'}), 400
        
        user = create_user(data['username'], data['password'], user_type='student')
        if not user:
            return jsonify({'error': 'Failed to create student user'}), 400
        
        return jsonify({'message': f'Student {user.username} successfully created with id {user.id}'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
