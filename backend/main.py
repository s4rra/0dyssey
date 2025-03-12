from flask import Flask, jsonify, request
from flask_cors import CORS
import supabase
import os


app = Flask(__name__)
CORS(app)  

SUPABASE_URL = "http://sarra.tailefeb94.ts.net:8000/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("userName")
    chosen_skill_level = data.get("chosenSkillLevel") 
    
    # print(f"Incoming data: {data}")
    # print(f"Email: {email}, Password: {password}, Username: {username}, Skill Level: {chosen_skill_level}")

    if not email or not password or not username or not chosen_skill_level:
        return jsonify({"error": "Email, password, username, and skill level are required"}), 400

    try:

        # print(f"Inserting user: Email={email}, Username={username}, Skill Level={chosen_skill_level}")

       
        existing_user = supabase_client.from_("User").select("Email").eq("Email", email).execute()
        if existing_user.data:
            return jsonify({"error": "Email already registered"}), 400

        response = supabase_client.from_("User").insert({
            "Email": email,
            "Password": password,
            "userName": username,
            "chosenSkillLevel": chosen_skill_level 
        }).execute()
        
        # print(f"Supabase response: {response}")

        return jsonify({"message": "User created successfully"}), 201

    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({"error": str(e)}), 500
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        print(f"Logging in user: {email}")

        response = supabase_client.from_("User").select("userID").eq("Email", email).eq("Password", password).execute()

        print(f"Login response: {response}")

        if response.data:
            return jsonify({"message": "Login successful", "user_id": response.data[0]["userID"]}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        # print(f"Login error: {e}")  
        return jsonify({"error": str(e)}), 500
@app.route("/skill-levels", methods=["GET"])
def get_skill_levels():
    try:
        response = supabase_client.from_("RefSkillLevel").select("*").execute()
        # print("Fetched skill levels:", response.data)
        return jsonify(response.data), 200
    except Exception as e:
        print(f"Error fetching skill levels: {e}")
        return jsonify({"error": str(e)}), 500
@app.route('/courses', methods=['GET'])
def get_courses():
    try:
        response = supabase_client.table("RefUnit").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/courses', methods=['POST'])
def add_course():
    try:
        data = request.get_json()
        new_course = {
            "unitID": data.get("unitID"),
            "unitName": data.get("unitName"),
        }
        response = supabase_client.table("RefUnit").insert(new_course).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8080)
