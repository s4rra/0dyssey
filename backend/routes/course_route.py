from flask import Blueprint, request, jsonify
from services.course_service import CourseService
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
