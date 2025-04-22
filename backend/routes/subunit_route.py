from flask import Blueprint, request, jsonify
from services.subunit_service import SubunitService
from utils.auth import verify_token

subunit_bp = Blueprint("subunit_bp", __name__)


@subunit_bp.route("/subunit/<int:subunit_id>", methods=["GET"])
def get_subunit_content(subunit_id):
    # Verify the user's token
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    user_id = None
    if isinstance(user, dict):
        user_id = user.get('userID') or user.get('user_id') or user.get('id')
    elif hasattr(user, 'userID'):
        user_id = user.userID
    elif hasattr(user, 'id'):
        user_id = user.id
    
    if not user_id:
        return jsonify({"error": "User ID not found"}), 400
    
    # Check if the user can access this subunit
    access_result, access_status = SubunitService.can_access_subunit(user_id, subunit_id)
    
    # If access is denied, return the error
    if access_status != 200 or not access_result.get('accessible', False):
        return jsonify(access_result), access_status
    
    # If access is allowed, get the content
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


@subunit_bp.route("/subunits/<int:subunit_id>/complete", methods=["POST"])
def mark_subunit_complete(subunit_id):
    print(f"Received request to mark subunit {subunit_id} as complete")
    
    # Verify the user's token
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        print(f"Authentication failed: {auth_result}")
        return jsonify(auth_result[0]), auth_result[1]
    
    # Get user ID from auth result
    user = auth_result
    print(f"Auth result: {user}")
    
    # Extract user ID based on your auth structure
    # Let's try multiple common formats
    user_id = None
    if isinstance(user, dict):
        user_id = user.get('userID') or user.get('user_id') or user.get('id')
    elif hasattr(user, 'userID'):
        user_id = user.userID
    elif hasattr(user, 'id'):
        user_id = user.id
    
    print(f"Extracted user_id: {user_id}")
    
    if not user_id:
        print("User ID not found in auth result")
        return jsonify({"error": "User ID not found"}), 400
        
    # Mark the subunit as completed
    print(f"Calling SubunitService.mark_subunit_completed({user_id}, {subunit_id})")
    result, status_code = SubunitService.mark_subunit_completed(user_id, subunit_id)
    print(f"Service result: {result}, status: {status_code}")
    
    return jsonify(result), status_code