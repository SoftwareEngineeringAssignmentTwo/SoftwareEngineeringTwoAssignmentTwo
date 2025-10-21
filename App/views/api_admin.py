from flask import Blueprint, jsonify, request
from App.controllers import (staff_log_hours, 
                            request_confirmation, 
                            view_leaderboard,
                            view_accolades,
                            staff_confirm_hours,    
                            staff_reject_hours,
                            update_leaderboard)

listings_views = Blueprint('api_admin_views', __name__, template_folder='../templates')

@listings_views.route('/api/log_hours', methods=['POST'])
def api_staff_log_hours():
    data = request.json
    log = staff_log_hours(data['staff_username'], data['student_username'], data['hours'], data['activity'])
    if not log:
        return jsonify({'error': 'Failed to log hours'}), 400
    return jsonify({'message': f"Logged {log.hoursLogged} hours for student ID {log.studentID} with log ID {log.logID}"}), 201

@listings_views.route('/api/request_confirmation', methods=['PUT'])     
def api_request_confirmation():
    data = request.json
    log = request_confirmation(data['student_username'], data['activity_log_id'])
    if not log:
        return jsonify({'error': 'Failed to request confirmation'}), 400
    return jsonify({'message': f"Requested confirmation for log ID {log.logID}"}), 200

@listings_views.route('/api/leaderboard', methods=['GET'])
def api_view_leaderboard():
    leaderboard = view_leaderboard()
    return jsonify(leaderboard), 200    

@listings_views.route('/api/accolades/<student_username>', methods=['GET'])
def api_view_accolades(student_username):
    accolades_data = view_accolades(student_username)
    if not accolades_data:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(accolades_data), 200

@listings_views.route('/api/staff/confirm_hours', methods=['PUT'])
def api_staff_confirm_hours():
    data = request.json
    log = staff_confirm_hours(data['staff_username'], data['activity_log_id'])
    if not log:
        return jsonify({'error': 'Failed to confirm hours'}), 400
    return jsonify({'message': f"Confirmed hours for log ID {log.logID}"}), 200         

@listings_views.route('/api/staff/reject_hours', methods=['PUT'])
def api_staff_reject_hours():
    data = request.json
    log = staff_reject_hours(data['staff_username'], data['activity_log_id'])
    if not log:
        return jsonify({'error': 'Failed to reject hours'}), 400
    return jsonify({'message': f"Rejected hours for log ID {log.logID}"}), 200

@listings_views.route('/api/update_leaderboard', methods=['PUT'])
def api_update_leaderboard():
    update_leaderboard()
    return jsonify({'message': 'Leaderboard updated successfully'}), 200            

