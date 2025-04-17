from flask import Blueprint, jsonify
from services.objective_service import ObjectiveService
from utils.auth import verify_token

objective_bp = Blueprint("objective_bp", __name__)

@objective_bp.route("/objectives", methods=["GET"])
def get_objectives():
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]

    user = auth_result
    result, status_code = ObjectiveService.get_user_objectives(user["id"])
    return jsonify(result), status_code

@objective_bp.route("/objectives/complete/<int:subunit_id>", methods=["POST"])
def complete_objective(subunit_id):
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]

    user = auth_result
    result, status_code = ObjectiveService.complete_objective(user["id"], subunit_id)
    return jsonify(result), status_code