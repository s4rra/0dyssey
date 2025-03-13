import os
import supabase
import functions
import json
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api #i will use resource later
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
api = Api(app) #to organise API routes, sinstead of using @app.route for every endpoint
CORS(app)#allow react to make requests to BE

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

@app.route('/subunits/<int:subunit_id>/questions', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_subunit_questions(subunit_id):
    try:
        # Fetch questions from the database for the given subunit
        response = supabase_client.from_("Question").select("*").eq("lessonID", subunit_id).execute()
        return jsonify(response.data), 200
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/subunits/<int:subunit_id>/generate-questions', methods=['POST', 'OPTIONS'])
@cross_origin()
def get_generate_questions(subunit_id):
    try: # Fetch subunit details
        subunit_response = supabase_client.from_("RefSubUnit").select("subUnitDescription").eq("subUnitID", subunit_id).execute()
        if not subunit_response.data:
            return jsonify({"error": "Subunit not found"}), 404
        subunit_description = subunit_response.data[0]["subUnitDescription"]
        # Fetch user's skill level
        user_id = request.json.get("user_id")
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        user_response = supabase_client.from_("User").select("chosenSkillLevel").eq("userID", user_id).execute()
        if not user_response.data:
            return jsonify({"error": "User not found"}), 404

        skill_level_id = user_response.data[0]["chosenSkillLevel"]
        skill_level_response = supabase_client.from_("RefSkillLevel").select("skillLevel").eq("skillLevelID", skill_level_id).execute()
        if not skill_level_response.data:
            return jsonify({"error": "Skill level not found"}), 404

        skill_level = skill_level_response.data[0]["skillLevel"]
        
        #Calling
        questions = functions.generate_questions(subunit_description, skill_level)
        if not isinstance(questions, list):#note
            return jsonify({"error": "Invalid AI response format"}), 500
        store_result = functions.store_generated_questions(questions, skill_level_id, subunit_id,supabase_client)
        #returning store_result for testing, questions to be used in FE
        return jsonify({"questions": questions, "store_result": store_result}), 200
    
    except Exception as e:
        print(f"Error getting generate input: {e}")
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(port=8080)