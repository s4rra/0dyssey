from flask import Blueprint, request, jsonify
from services.answer_service import *
from services.user_service import *
from utils.auth import verify_token

answer_bp = Blueprint("answer_bp", __name__)

@answer_bp.route("/submit-answers", methods=["POST"])
def submit_answers():
    try:
        auth_result = verify_token()
        if "error" in auth_result:
            return jsonify(auth_result), 401

        user_id = auth_result["id"]
        user_profile, status = UserService.get_user_profile(user_id)
        if status != 200:
            return jsonify(user_profile), status

        skill_level = user_profile["currentSkillLevel"]
        answers_data = request.get_json()

        # Clean delegation to service
        results = Answer.submit_answers(user_id, answers_data, skill_level)

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
