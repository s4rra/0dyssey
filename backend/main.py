from flask import Flask, jsonify, request
from flask_cors import CORS
import supabase
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json
from flask_cors import cross_origin

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
def generate_questions(subunit_id):
    try:
        # Fetch subunit details
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

        # Generate questions using Gemini API
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=f"""
                        Act as an energetic programming instructor generating Python questions for students aged 10-17.
                        Prioritize strict JSON formatting while maintaining an engaging tone.
                        You will receive **subunit details** to ensure the questions match the topic.

                        📌 **Skill Level Rules:**
                        - **Beginner:** Use only the following question types: `fill_in_the_blanks`, `multiple_choice`, `drop_down`.
                        - **Intermediate:** Include some `coding` questions along with theory-based ones.
                        - **Expert:** Only return `coding` questions.

                        📌 **Expected Input JSON**
                        ```json
                        {{
                          "subunit_description": "{subunit_description}",
                          "skill_level": "{skill_level}"
                        }}
                        ```
                    """),
                ],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.5,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
        )

        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )

        # Parse the generated questions
        generated_questions = json.loads(response.text)["questions"]

        # Store generated questions in the database
        for question in generated_questions:
            supabase_client.from_("Question").insert({
                "questionTypeID": 1,  # Replace with the appropriate question type ID
                "skillLevelID": skill_level_id,
                "lessonID": subunit_id,
                "questionText": question["text"],
                "generated": True,
                "questionCode": question.get("code", ""),
                "Tags": json.dumps(question.get("tags", []))
            }).execute()

        return jsonify(generated_questions), 200

    except Exception as e:
        print(f"Error generating questions: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8080)