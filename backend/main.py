import base64
import os
import json
import supabase
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
from google import genai
from google.genai import types
from supabase import create_client

load_dotenv()
app = Flask(__name__)
CORS(app)

SUPABASE_URL = "http://sarra.tailefeb94.ts.net:8000/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

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

@app.route('/questions', methods=['Get'])
def get_questions():
    user_data = fetch_user_data()
    questions = generate(user_data)
    #testing
    print ( f"questions: {questions}, user data:{user_data}")
    return jsonify(questions)

def fetch_user_data():
    try:
        user_id = 4  # Hardcoded for testing

        response = (
            supabase_client.table("User")
            .select("RefSkillLevel(skillLevel)", "RefSubUnit(subUnitDescription)", "RefUnit(unitDescription)")
            .eq("userID", user_id)
            .execute()
        )

        if not response.data or len(response.data) == 0:
            return None

        # required as dictionary
        user_data = response.data[0]
        return {
            "unit": user_data["RefUnit"]["unitDescription"],
            "subunit": user_data["RefSubUnit"]["subUnitDescription"],
            "skill_level": user_data["RefSkillLevel"]["skillLevel"]
        }

    except Exception as e:
        return {"error": str(e)}

def generate(user_data):
    if not user_data:
       return {"error": "user data not found or invalid"}

    user_prompt = f"unit: {user_data['unit']}, sub unit: {user_data['subunit']}, skill level: {user_data['skill_level']}"
    
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_prompt),],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.5,
        top_k=40,
        max_output_tokens=1000,
        response_mime_type="application/json",
        system_instruction=[
            types.Part.from_text(
                text="""Act as an energetic teacher generating Python questions in JSON format for students 10-17. Prioritize accurate JSON
                structure while maintaining an engaging tone. Unit and sub unit details will be specified for context of the questions.

Beginner skill level: Generate exactly 5 questions including a mix of
1. Fill-in-the-blanks
2. drop-down
3. Multiple Choice Questions (MCQs)

Intermediate skill level: Generate exactly 5 questions including a mix of
1. Fill-in-the-blanks
2. Drop down
3. MCQs
4. Written Code Questions

Expert skill level: Generate exactly 5 questions, all of them must be written code questions.

Note: 
- All options should be randomized in order.
- Coding questions should be specific.
- For drop-down questions only, use placeholders like \"[BLANK_1]\", \"[BLANK_2]\", etc., within the question text to indicate where dropdowns should appear.
- For fill-in-the-blanks questions, represent the blanks with a series of underscore characters (e.g., \"_____\"). Do not use \"[BLANK]\" for fill-in-the-blanks.


Expected input:
```json
{
  \"unit\": \"\",
  \"subunit\": \"\",
  \"skill_level\": \"\"
}
```

Bellow is the output format structure for each question type, follow a json object stricket format:
 {
  \"question(number)\": {
    \"type\": \"fill_in_the_blanks\",
    \"question\": \"question text with blank/s\",
    \"options\": {
      \"a\": \"\",
      \"b\": \"\",
      \"c\": \"\",
      \"d\": \"\"
    },
    \"correct_answer\": \"a,b,c or d\"
  },
  \"question(number)\": {
    \"type\": \"multiple_choice\",
    \"question\": \"question text\",
    \"options\": {
      \"a\": \"\",
      \"b\": \"\",
      \"c\": \"\",
      \"d\": \"\"
    },
    \"correct_answer\": \"a,b,c,or d\"
  },
 \"question(number)\": {
\"type\": \"drop_down\",
\"question\": \"question text with [BLANK_1], [BLANK_2], etc.\",
\"dropdowns\": [
{
\"placeholder\": \"[BLANK_1]\",
\"options\": [\"option1\", \"option2\", \"option3\"],
\"correctAnswer\": \"option\"
},
{
\"placeholder\": \"[BLANK_2]\",
\"options\": [\"choiceA\", \"choiceB\", \"choiceC\", \"choiceD\"],
\"correctAnswer\": \"choice\"
}
// Add more dropdowns for each placeholder in question
]
},
  \"question(number)\": {
    \"type\": \"coding\",
    \"question\": \"question text\",
    \"expected_output\": \"\",
    \"constraints\": \"\"
  }
}"""
            ),
        ],
    )
    generated_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        generated_text += chunk.text
        
    try:
        questions_json = json.loads(generated_text)
        return questions_json
    except json.JSONDecodeError:
        return {"error": "failed to parse AI response"}

if __name__ == '__main__':
    app.run(port=8080)