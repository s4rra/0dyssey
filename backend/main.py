from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
import supabase
import os
app = Flask(__name__)
CORS(app)

# Initialize Supabase client
SUPABASE_URL = "http://sarra.tailefeb94.ts.net:8000/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    dob = data.get("dob")
    chosen_skill_level = data.get("chosenSkillLevel")

    try:
        existing_user = supabase.table("User").select("*").eq("Email", email).execute()
        if len(existing_user.data) > 0:
            return jsonify({"error": "User already exists"}), 409

        response = supabase.table("User").insert({
            "Email": email,
            "Password": password,
            "userName": username,
            "DOB": dob,
            "chosenSkillLevel": chosen_skill_level,
            "Points": 0,
            "streakLength": 0,
            "currentUnit": 1,
            "currentSubUnit": 1
        }).execute()

        return jsonify({"message": "User created successfully", "user": response.data[0]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Fetch user from Supabase
    user_data = supabase_client.table("User").select("*").eq("Email", email).eq("Password", password).execute()

    if user_data.data:  # Check if data exists
        return jsonify({"message": "Login successful", "user": user_data.data[0]}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


if __name__ == '__main__':
    app.run(debug=True)
