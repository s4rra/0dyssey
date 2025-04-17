from flask import Blueprint, request, jsonify
from services.user_service import UserService
from utils.auth import verify_token

user_bp = Blueprint("user_bp", __name__)
# Uses JWT token authentication for protected routes

@user_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    result, status_code = UserService.signup(
        data.get("Email"),
        data.get("Password"),
        data.get("userName"),
        data.get("chosenSkillLevel"),
        data.get("DOB")
    )
    return jsonify(result), status_code

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    result, status_code = UserService.login(data.get("email"), data.get("password"))
    return jsonify(result), status_code

@user_bp.route("/user-profile", methods=["GET"])
def get_user_profile():
    auth_result = verify_token()
    # If verify_token returns a tuple, it's an error response
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]

    user = auth_result
    result, status_code = UserService.get_user_profile(user)
    return jsonify(result), status_code
@user_bp.route("/profile-pictures", methods=["GET"])
def get_profile_pictures():
    try:
        auth_result = verify_token()
        # If verify_token returns a tuple, it's an error response
        if isinstance(auth_result, tuple):
            # For non-authenticated users, just get all profile pictures without availability info
            result, status_code = UserService.get_profile_pictures()
            return jsonify(result), status_code
        
        # For authenticated users, get profile pictures with availability info
        user = auth_result
        result, status_code = UserService.get_profile_pictures(user["id"])
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@user_bp.route("/update-profile-picture", methods=["POST"])
def update_profile_picture():
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    data = request.json
    result, status_code = UserService.update_profile_picture(user["id"], data.get("pictureID"))
    return jsonify(result), status_code