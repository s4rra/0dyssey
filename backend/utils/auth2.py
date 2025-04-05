from functools import wraps
from flask import request, jsonify
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        try:
            token = auth_header.split(" ")[1]
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            user = {
                "userID": decoded_token["userID"],
                "currentSkillLevel": decoded_token.get("currentSkillLevel"),
                "id": decoded_token["userID"]  # 🧠 Add this for backward compatibility
            }

            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    return decorated
