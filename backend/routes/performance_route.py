from flask import Blueprint, request, jsonify
from services.performance_service import PerformanceService
from services.user_service import UserService
from utils.auth import verify_token

performance_bp = Blueprint("performance_bp", __name__)

@performance_bp.route("/performance/submit/<int:unit_id>/<int:subunit_id>", methods=["POST"])
def submit_performance(unit_id, subunit_id):
    try:
        user = verify_token()
        if isinstance(user, tuple):
            return jsonify(user[0]), user[1]

        user_id = user["id"]
        answers_data = request.get_json()

        if not answers_data or not isinstance(answers_data, list):
            return jsonify({"error": "Invalid request data. Expected list of answers."}), 400

        service = PerformanceService(user_id)
        result = service.update_performance(unit_id, subunit_id, answers_data)

        if not result.get("success"):
            return jsonify({"error": result.get("error", "Failed to update performance")}), 500

        return jsonify({
            "message": "Performance updated successfully",
            "performanceID": result.get("performanceID")
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@performance_bp.route("/performance/skill-level", methods=["POST"])
def update_skill_level():
    try:
        user = verify_token()
        if isinstance(user, tuple):
            return jsonify(user[0]), user[1]

        user_id = user["id"]
        data = request.get_json()
        if not data or "skillLevel" not in data:
            return jsonify({"error": "Missing skillLevel in request"}), 400

        new_level = data.get("skillLevel")
        service = PerformanceService(user_id)
        result = service.update_skill_level(new_level)

        if not result.get("success"):
            return jsonify({"error": result.get("error", "Failed to update skill level")}), 500

        return jsonify({
            "message": "Skill level updated successfully",
            "newLevel": result.get("newLevel")
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@performance_bp.route("/performance/history/<int:subunit_id>", methods=["GET"])
def get_subunit_history(subunit_id):
    try:
        user = verify_token()
        if isinstance(user, tuple):
            return jsonify(user[0]), user[1]

        user_id = user["id"]
        limit = request.args.get("limit", default=5, type=int)
        service = PerformanceService(user_id)
        history = service.get_performance_history(subunit_id, limit)

        return jsonify(history), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@performance_bp.route("/performance/unit/<int:unit_id>", methods=["POST"])
def analyze_unit_performance(unit_id):
    try:
        user = verify_token()
        if isinstance(user, tuple):
            return jsonify(user[0]), user[1]

        user_id = user["id"]
        user_profile, status = UserService.get_user_profile(user)
        if status != 200:
            return jsonify(user_profile), status

        skill_level = user_profile["chosenSkillLevel"]

        service = PerformanceService(user_id)
        result = service.model_feedback(unit_id, skill_level)

        if not result.get("success"):
            return jsonify({"error": result.get("error", "Failed to generate AI feedback")}), 500

        return jsonify({
            "message": "AI feedback generated successfully",
            "feedback": result.get("feedback")
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#############
