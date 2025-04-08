from flask import Blueprint, request, jsonify
from services.answer_service import Answer
from services.user_service import UserService
from utils.auth import verify_token

answer_bp = Blueprint("answer_bp", __name__)

@answer_bp.route("/submit-answer", methods=["POST"])
def submit_answer():
    try:
        auth_result = verify_token()
        if isinstance(auth_result, tuple) and "error" in auth_result[0]:
            return jsonify(auth_result[0]), auth_result[1]
        if "error" in auth_result:
            return jsonify(auth_result), 401

        user_id = auth_result["id"]
        data = request.get_json()
        
        # Get user skill level
        user_profile, status = UserService.get_user_profile(user_id)
        if status != 200:
            return jsonify(user_profile), status

        skill_level = user_profile["currentSkillLevel"]
        
        answer = Answer(data, user_id, skill_level)
        validate_answer(answer)
        apply_scoring(answer)
        result = persist_answer(answer)
        
        if not result["success"]:
            return jsonify({"error": result["error"]}), result.get("status", 500)
            
        return jsonify({
            "success": True,
            "data": {
                "isCorrect": answer.is_correct,
                "points": answer.points,
                "feedback": answer.feedback,
                "hint": answer.hint
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@answer_bp.route("/submit-answers", methods=["POST"])
def submit_answers():
    try:
        auth_result = verify_token()
        if isinstance(auth_result, tuple) and "error" in auth_result[0]:
            return jsonify(auth_result[0]), auth_result[1]
        if "error" in auth_result:
            return jsonify(auth_result), 401

        user_id = auth_result["id"]
        
        # Get user skill level
        user_profile, status = UserService.get_user_profile(user_id)
        if status != 200:
            return jsonify(user_profile), status

        skill_level = user_profile["currentSkillLevel"]
        
        # Get the list of answers
        answers_data = request.get_json()
        if not isinstance(answers_data, list):
            return jsonify({"error": "expecting a list of answers"}), 400
        
        results = Answer.submit_answers(user_id, answers_data, skill_level)
        
        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500