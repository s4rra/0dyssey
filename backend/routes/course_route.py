from flask import Blueprint, request, jsonify
from services.course_service import CourseService
from utils.auth import verify_token

course_bp = Blueprint("course_bp", __name__)

@course_bp.route("/courses", methods=["GET"])
def get_courses():
    return jsonify(CourseService.get_courses())

@course_bp.route("/courses", methods=["POST"])
def add_course():
    user = verify_token()
    if isinstance(user, dict):
       return user

    data = request.get_json()
    return jsonify(CourseService.add_course(data))
