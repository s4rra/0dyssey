from flask import Blueprint, request, jsonify
#from services.question_service import QuestionService
from utils.auth import verify_token
from prompt import *

# API endpoints for questions, protected using JWT authentication

question_bp = Blueprint("question_bp", __name__)

@question_bp.route("/subunits/<int:subunit_id>/questions", methods=["GET"])
def get_subunit_questions(subunit_id):
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = Questions.get_questions(subunit_id, user)
    return jsonify(result), status_code

@question_bp.route("/subunits/<int:subunit_id>/generate-questions", methods=["POST"])
def generate_questions(subunit_id):
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = Questions.generate_questions(subunit_id, user)
    return jsonify(result), status_code

""" @question_bp.route("/check-answers", methods=["POST"])
def check_answers():
    auth_result = verify_token()
    # If verify_token returns a tuple, it's an error response
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]

    user = auth_result
    data = request.json
    result, status_code = Questions.check_coding(input)
    return jsonify(result), status_code

 """