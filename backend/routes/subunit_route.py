from flask import Blueprint, request, jsonify
from services.subunit_service import SubunitService
from utils.auth import verify_token

subunit_bp = Blueprint("subunit_bp", __name__)

@subunit_bp.route("/subunit/<int:subunit_id>", methods=["GET"])
def get_subunit_content(subunit_id):
    data, status_code = SubunitService.get_subunit_content(subunit_id)
    return jsonify(data), status_code

@subunit_bp.route("/subunit", methods=["POST"])
def add_subunit():
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    data = request.get_json()
    result, status_code = SubunitService.add_subunit(data)
    return jsonify(result), status_code