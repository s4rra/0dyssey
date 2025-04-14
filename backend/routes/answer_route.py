import json
from flask import Blueprint, request, jsonify
from services.answer_service import *
from services.user_service import *
from utils.auth import verify_token

answer_bp = Blueprint("answer_bp", __name__)

@answer_bp.route("/submit-answers", methods=["POST"])
def submit_answers():
    try:
        auth_result = verify_token()
        if isinstance(auth_result, tuple):
            return jsonify(auth_result[0]), auth_result[1]
        user_id = auth_result["id"]
        
        user = auth_result
        print(F"NO ISSUE WITH USER ID :{user_id}")
        user_profile, status = UserService.get_user_profile(user)
        print(f"no isse with user_profile: {user_profile}")
        if status != 200:
            return jsonify(user_profile), status

        skill_level = user_profile["chosenSkillLevel"]
        raw_data = request.get_data(as_text=True)

        try:
            answers_data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON: {str(e)}"}), 400

        if not isinstance(answers_data, list):
            return jsonify({"error": "payload must be a list of answers"}), 400

        results = Answer.submit_answers(user_id, answers_data, skill_level)
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@answer_bp.route("/hint-used", methods=["POST"])
def hint_used():
    try:
        auth_result = verify_token()
        if isinstance(auth_result, tuple):
            return jsonify(auth_result[0]), auth_result[1]
        user_id = auth_result["id"]

        result = ScoreCalculator.deduct_for_hint(user_id)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
