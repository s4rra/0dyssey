import os
import jwt
import uuid
from datetime import datetime, timezone, timedelta
from config.settings import supabase_client
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")


class UserService:
    @staticmethod
    def signup(email, password, username, chosen_skill_level, dob):
        try:
            # Check if email already exists in User table
            existing_user = supabase_client.from_("User").select("userID").eq("Email", email).execute()
            if existing_user.data:
                return {"error": "Email already registered."}, 400

            # Manually generate a userID using UUID
            user_id = str(uuid.uuid4())

            # Insert user into User table
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
            user_response = supabase_client.from_("User").select(
                "userID, Password, streakLength, lastLogin"
            ).eq("Email", email).execute()

            user_data = user_response.data
            if not user_data:
                return {"error": "Invalid email or password"}, 401

            user = user_data[0]

            # Password check
            if not check_password_hash(user["Password"], password):
                return {"error": "Invalid password"}, 401

            # Streak calculation
            current_date = datetime.now(timezone.utc).date()
            streak_length = user.get("streakLength", 0)
            last_login = user.get("lastLogin")

            if last_login:
                last_login = datetime.fromisoformat(last_login).date()

            if last_login is None:
                new_streak = 0
            elif last_login == current_date:
                new_streak = streak_length
            elif (current_date - last_login).days == 1:
                new_streak = streak_length + 1
            else:
                new_streak = 0

            # Update user streak info
            supabase_client.from_("User").update({
                "streakLength": new_streak,
                "lastLogin": current_date.isoformat()
            }).eq("userID", user["userID"]).execute()

            # Generate JWT token
            token_payload = {
                "userID": user["userID"],
                "exp": datetime.now(timezone.utc) + timedelta(hours=2)
            }
            access_token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

            return {
                "message": "Login successful",
                "access_token": access_token,
                "streak": new_streak
            }, 200

        except Exception as e:
            print(f"Login error: {e}")
            return {"error": str(e)}, 500

    @staticmethod
    def get_user_profile(user):
        try:
            user_id = user["id"]
            print("profile got user id")
            response = (
                supabase_client
                .table("User")
                .select("*, RefUnit(unitDescription), RefSubUnit(subUnitDescription)")
                .eq("userID", user_id)
                .single()  #one row only
                .execute()
            )
            if not response.data:
                return {"error": "User not found"}, 404

            return response.data, 200  #no need for [0] after .single()

        except Exception as e:
            return {"error": str(e)}, 500
    ###########
    @staticmethod
    def get_user_profile2(user):
        try:
            user_id = user["id"]  # extract userID from session

            # Fetch user data with profile picture join
            response = supabase_client.from_("User") \
                .select("*, ProfilePictures!inner(pictureID, imagePath, displayName)") \
                .eq("userID", user_id) \
                .execute()

            if not response.data:
                return {"error": "User not found"}, 404

            return response.data, 200  #no need for [0] after .single()

        except Exception as e:
            return {"error": str(e)}, 500
    ###########
    
    @staticmethod
    def get_profile_pictures():
        try:
            response = supabase_client.from_("ProfilePictures").select("*").execute()
            return response.data, 200
        except Exception as e:
            print(f"Error fetching profile pictures: {e}")
            return {"error": str(e)}, 500

    @staticmethod
    def update_profile_picture(user_id, picture_id):
        try:
            response = supabase_client.from_("User").update({
                "profilePicture": picture_id
            }).eq("userID", user_id).execute()

            if not response.data:
                return {"error": "Failed to update profile picture"}, 404

            return {"message": "Profile picture updated successfully"}, 200
        except Exception as e:
            print(f"Error updating profile picture: {e}")
            return {"error": str(e)}, 500
