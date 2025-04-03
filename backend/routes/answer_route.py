from flask import Blueprint, request, jsonify
from services.answer_service import *
from services.user_service import *
from utils.auth import verify_token

answer_bp = Blueprint("answer_bp", __name__)

@answer_bp.route("/submit-answers", methods=["POST"])
def submit_answers():
    # Verify token and get user
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    user_profile, status = UserService.get_user_profile(user)
    if status != 200:
        return jsonify(user_profile), status
    
    # Get submitted answers from request
    answers_data = request.json
    
    # Submit answers
    results = Answer.submit_answers(user_profile['userID'], answers_data)
    
    return jsonify({
        "message": "Answers submitted successfully",
        "results": results
    }), 200