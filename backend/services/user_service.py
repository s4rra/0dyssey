import os
import jwt
import uuid
from datetime import datetime, timezone, timedelta
from config.settings import supabase_client
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

#handles signup and login processes
class UserService:
    @staticmethod
    def signup(email, password, username, chosen_skill_level, dob):
        try:
            #Check if email already exists in User table
            existing_user = supabase_client.from_("User").select("userID").eq("Email", email).execute()
            if existing_user.data:
                return {"error": "Email already registered."}, 400

            # manually generate a userID using UUID
            user_id = str(uuid.uuid4())

            # Insert user manually into User table with explicit userID
            response = supabase_client.from_("User").insert({
                "userID": user_id,
                "Email": email,
                "Password": generate_password_hash(password),
                "userName": username,
                "chosenSkillLevel": chosen_skill_level,
                "DOB": dob,
                "Points": 0,
                "streakLength": 0
            }).execute()
            if not response.data:
                return {"error": "Failed to create user."}, 500
        
            return {"message": "Signup successful."}, 201

        except Exception as e:
            print(f"Signup error: {e}")
            return {"error": str(e)}, 500

    @staticmethod
    def login(email, password):
        try:
            user_response = supabase_client.from_("User").select("userID, Password").eq("Email", email).execute()
            user_data = user_response.data
            

            if not user_data:
                return {"error": "Invalid email or password"}, 401  # User not found

            user = user_data[0]

            # Check if password matches (hashed check)
            if not check_password_hash(user["Password"], password):
                return {"error": "Invalid email or password"}, 401

            # JWT token for session authentication
            token_payload = {
               "userID": user["userID"],
               "exp": datetime.now(timezone.utc) + timedelta(hours=2)
            }
            access_token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
            
            print("JWT_SECRET_KEY during encoding:", SECRET_KEY)#just used when testing

            return {"message": "Login successful", "access_token": access_token}, 200

        except Exception as e:
            print(f"Login error: {e}")
            return {"error": str(e)}, 500

    @staticmethod
    def get_user_profile(user):
        # Fetch user details from the "User" table using the user session (JWT token)

        try:
            user_id = user["id"]  # extract userID from session

            # Fetch user data from our user table
            response = supabase_client.table("User").select("*").eq("userID", user_id).execute()
            if not response.data:
                return {"error": "User not found"}, 404

            return response.data[0], 200

        except Exception as e:
            return {"error": str(e)}, 500