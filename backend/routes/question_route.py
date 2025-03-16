from flask import Blueprint, request, jsonify
from services.question_service import QuestionService
from utils.auth import verify_token

#api endpoints for questions, uses session authentication
question_bp = Blueprint("question_bp", __name__)

@question_bp.route("/subunits/<int:subunit_id>/questions", methods=["GET"])
def get_subunit_questions(subunit_id):
    user = verify_token()
    if isinstance(user, dict):
        return user

    return jsonify(QuestionService.get_questions(subunit_id, user))

@question_bp.route("/subunits/<int:subunit_id>/generate-questions", methods=["POST"])
def generate_questions(subunit_id):
    user = verify_token()
    if isinstance(user, dict):
        return user
    
    return jsonify(QuestionService.generate_questions(subunit_id, user))

@question_bp.route("/check-answers", methods=["POST"])
def check_answers():
    user = verify_token()
    if isinstance(user, dict):
       return user

    data = request.json
    return jsonify(QuestionService.check_answers(user, data.get("userAnswers")))

