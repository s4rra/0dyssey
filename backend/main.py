from flask import Flask, jsonify, request
from flask_cors import CORS
import supabase
import os
from dotenv import load_dotenv
import json


load_dotenv()
app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("userName")
    chosen_skill_level = data.get("chosenSkillLevel")

    if not email or not password or not username or not chosen_skill_level:
        return jsonify({"error": "Email, password, username, and skill level are required"}), 400

    try:
        existing_user = supabase_client.from_("User").select("Email").eq("Email", email).execute()
        if existing_user.data:
            return jsonify({"error": "Email already registered"}), 400

        response = supabase_client.from_("User").insert({
            "Email": email,
            "Password": password,
            "userName": username,
            "chosenSkillLevel": chosen_skill_level
        }).execute()

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
        response = supabase_client.from_("User").select("userID").eq("Email", email).eq("Password", password).execute()

        if response.data:
            return jsonify({"message": "Login successful", "user_id": response.data[0]["userID"]}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/skill-levels", methods=["GET"])
def get_skill_levels():
    try:
        response = supabase_client.from_("RefSkillLevel").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        print(f"Error fetching skill levels: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/courses', methods=['GET'])
def get_courses():
    try:
        # Fetch units with nested subunits
        response = supabase_client.from_("RefUnit").select("unitID, unitName, RefSubUnit(subUnitID, subUnitName)").execute()
        
        # Debugging: Print the fetched data
        print("Fetched courses with subunits:", response.data)

        return jsonify(response.data), 200
    except Exception as e:
        print("Error fetching courses:", e)
        return jsonify({"error": str(e)}), 500

# @app.route('/courses', methods=['POST'])
# def add_course():
#     try:
#         data = request.get_json()
#         new_course = {
#             "unitID": data.get("unitID"),
#             "unitName": data.get("unitName"),
#         }
#         response = supabase_client.table("RefUnit").insert(new_course).execute()
#         return jsonify(response.data), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/subunit/<int:subunit_id>', methods=['GET'])
def get_subunit_content(subunit_id):
    try:
        # Fetch the specific subunit with its content
        response = supabase_client.from_("RefSubUnit").select("subUnitID, subUnitName, subUnitContent").eq("subUnitID", subunit_id).execute()
        
        if not response.data:
            return jsonify({"error": "Subunit not found"}), 404
            
        subunit = response.data[0]
        
        # If the content is stored as JSON string, parse it
        if isinstance(subunit.get('subUnitContent'), str):
            try:
                subunit['subUnitContent'] = json.loads(subunit['subUnitContent'])
            except json.JSONDecodeError:
                # If it's not valid JSON, keep it as is
                pass
                
        return jsonify(subunit), 200
        
    except Exception as e:
        print(f"Error fetching subunit content: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=8080)