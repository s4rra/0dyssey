import os
from flask import request
import jwt
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
#authorization
#checks if a request has a valid JWT
def verify_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Missing or invalid token"}, 401

    try:
        token = auth_header.split(" ")[1]
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        print("JWT_SECRET_KEY during decoding:", SECRET_KEY)#just used when testing
        # Return user info dictionary
        return {"id": decoded_token["userID"]}

    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401

