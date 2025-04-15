from flask import Blueprint, request, jsonify
from services.bookmark_service import BookmarkService
from utils.auth import verify_token

bookmark_bp = Blueprint("bookmark_bp", __name__)

@bookmark_bp.route("/bookmark/<int:subunit_id>", methods=["POST"])
def add_bookmark(subunit_id):
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = BookmarkService.add_bookmark(user["id"], subunit_id)
    return jsonify(result), status_code

@bookmark_bp.route("/bookmark/<int:subunit_id>", methods=["DELETE"])
def remove_bookmark(subunit_id):
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = BookmarkService.remove_bookmark(user["id"], subunit_id)
    return jsonify(result), status_code

@bookmark_bp.route("/bookmarks", methods=["GET"])
def get_bookmarks():
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = BookmarkService.get_user_bookmarks(user["id"])
    return jsonify(result), status_code