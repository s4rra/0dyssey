from flask import Blueprint, request, jsonify
from services.question_service import *
from services.user_service import *
from utils.auth import verify_token

question_bp = Blueprint("question_bp", __name__)

@question_bp.route("/subunits/<int:subunit_id>/questions", methods=["GET"])
def get_subunit_questions(subunit_id):
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    user = auth_result
    user_profile, status = UserService.get_user_profile(user)
    if status != 200:
        return jsonify(user_profile), status
    
    result, status_code = Questions.get_questions(subunit_id, user_profile)
    return jsonify(result), status_code

@question_bp.route("/subunits/<int:subunit_id>/generate-questions", methods=["POST"])
def generate_questions(subunit_id):
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    user = auth_result
    user_profile, status = UserService.get_user_profile(user)
    if status != 200:
        return jsonify(user_profile), status
           
    result, status_code = Questions.generate_questions(subunit_id, user_profile)
    return jsonify(result), int(status_code)
