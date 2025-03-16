from flask import Blueprint, request, jsonify
from services.user_service import UserService
from utils.auth import verify_token

user_bp = Blueprint("user_bp", __name__)

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
    return jsonify(UserService.login(data.get("email"), data.get("password")))

@user_bp.route("/user-profile", methods=["GET"])
def get_user_profile():
    user = verify_token()
    if isinstance(user, dict):
        return user

    return jsonify(UserService.get_user_profile(user))
