from flask import Blueprint, request, jsonify
from services.mission_service import MissionService
from utils.auth import verify_token

mission_bp = Blueprint("mission_bp", __name__)

@mission_bp.route("/missions", methods=["GET"])
def get_missions():
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = MissionService.get_missions(user["id"])
    return jsonify(result), status_code

@mission_bp.route("/mission/<mission_id>", methods=["GET"])
def get_mission(mission_id):
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = MissionService.get_mission_details(user["id"], mission_id)
    return jsonify(result), status_code

@mission_bp.route("/mission/<mission_id>/answer", methods=["POST"])
def submit_answer(mission_id):
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    data = request.json
    answer = data.get("answer")
    
    result, status_code = MissionService.answer_mission(user["id"], mission_id, answer)
    return jsonify(result), status_code