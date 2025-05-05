from flask import Blueprint, request, jsonify
from services.mission_service import MissionService
from utils.auth import verify_token

mission_bp = Blueprint("mission_bp", __name__)

@mission_bp.route("/missions", methods=["GET"])
def get_missions():
    """Get all available missions"""
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    
    result, status_code = MissionService.get_missions(user["id"])
    return jsonify(result), status_code

@mission_bp.route("/missions/<int:mission_id>", methods=["GET"])
def get_mission_details(mission_id):
    """Get specific mission details"""
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = MissionService.get_mission_details(user["id"], mission_id)
    return jsonify(result), status_code

@mission_bp.route("/missions/<int:mission_id>/submit", methods=["POST"])
def submit_mission_answers(mission_id):
    """Submit answers for a mission"""
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    data = request.json
    answers = data.get("answers")
    
    result, status_code = MissionService.submit_answers(user["id"], mission_id, answers)
    return jsonify(result), status_code

@mission_bp.route("/missions/progress", methods=["GET"])
def get_user_mission_progress():
    """Get user's progress across all missions"""
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = MissionService.get_user_progress(user["id"])
    return jsonify(result), status_code