from flask import Blueprint, request, jsonify
from services.answer_service import Answer
from services.user_service import UserService
from utils.auth import verify_token

answer_bp = Blueprint("answer_bp", __name__)

@answer_bp.route("/submit-answers", methods=["POST"])
def submit_answers():
    print("✅ /api/submit-answers HIT")
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

        # The submit_answers method returns a dict with "results" key
        # Just pass it directly to jsonify
        results = Answer.submit_answers(user_id, answers_data, skill_level)
        return jsonify(results), 200


    except Exception as e:
        return jsonify({"error": str(e)}), 500