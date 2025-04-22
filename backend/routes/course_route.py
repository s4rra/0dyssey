from flask import Blueprint, request, jsonify
from services.course_service import CourseService
from services.subunit_service import SubunitService  # Add this import
from utils.auth import verify_token

course_bp = Blueprint("course_bp", __name__)

@course_bp.route("/courses", methods=["GET"])
def get_courses():
    data, status_code = CourseService.get_courses()
    return jsonify(data), status_code

@course_bp.route("/questions", methods=["GET"])
def get_questions():
    data, status_code = CourseService.get_questions()
    return jsonify(data), status_code

@course_bp.route("/courses", methods=["POST"])
def add_course():
    auth_result = verify_token()
    # If verify_token returns an error response, authentication failed.
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    data = request.get_json()
    result, status_code = CourseService.add_course(data)
    return jsonify(result), status_code

@course_bp.route("/user-progress", methods=["GET"])
def get_user_progress():
    # Verify the user's token
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    user_id = None
    if isinstance(user, dict):
        user_id = user.get('userID') or user.get('user_id') or user.get('id')
    elif hasattr(user, 'userID'):
        user_id = user.userID
    elif hasattr(user, 'id'):
        user_id = user.id
    
    if not user_id:
        return jsonify({"error": "User ID not found"}), 400
    
    # Get the user's progress
    result, status_code = SubunitService.get_user_progress(user_id)
    return jsonify(result), status_code