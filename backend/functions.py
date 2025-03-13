import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def generate_questions(subunit_description, skill_level):
    user_prompt = json.dumps({
    "subunit": subunit_description,
    "skill_level": skill_level
    })
    
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_prompt)],
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
                structure output while maintaining an engaging tone. subUnit details will be specified for context of the questions.

Beginner skill level: Generate exactly 5 questions. Use only the following question types:
1. Fill-in-the-blanks
2. drop-down
3. Multiple Choice Questions

Intermediate skill level: Generate exactly 5 questions. Use only the following question types:
1. Fill-in-the-blanks
2. Drop down
3. MCQs
4. Written Code Questions

Expert skill level: Generate exactly 5 questions, Use only the coding question type.

Note:
- All options should be randomized in order.
- Coding questions should be specific.
- For drop-down questions only, use placeholders like \"[BLANK_1]\", \"[BLANK_2]\", etc., within the question text to indicate where dropdowns should appear.
- For fill-in-the-blanks questions, represent the blanks with a series of underscore characters (e.g., _____). Do not use \"[BLANK]\" for fill-in-the-blanks..
-For fill_in_the_blanks questions, you can have 1 or 2 blanks to fill. in the options, one is correct(a,b,c, or d) and contains the filling of the blanks.
-question text shouldnt contain `'\", unless its for code formatting in the question.

Expected input:
```json
{
  \"subunit\": \"\",
  \"skill_level\": \"\"
}
```
Bellow is the output format structure for each question type:
 {
  \"question(number)\": {
    \"type\": \"fill_in_the_blanks\",
    \"question\": \"question text with blank/s\",
    \"options\": {
      \"a\": \"option, option\",
      \"b\": \"ans, ans\",
      \"c\": \"answer\",
      \"d\": \"answer, answer, answer\"
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
       return {"error": "Failed to parse AI response"}

def store_generated_questions(questions, skill_level_id, subunit_id, supabase_client):
    try:
        for question in questions:
            # needs review...
            # Prepare question data
            question_data = {
                "questionTypeID": 1,  # Placeholder, should be dynamic
                "skillLevelID": skill_level_id,
                "lessonID": subunit_id,
                "questionText": question["question"],
                "generated": True,
                "questionCode": question.get("expected_output", ""),
                "Tags": json.dumps(question.get("tags", [])) if "tags" in question else "[]"
            }

            # Insert into Supabase
            supabase_client.from_("Question").insert(question_data).execute()
        
        return {"message": "Questions stored successfully"}
    
    except Exception as e:
        print(f"Error storing questions: {e}")
        return {"error": str(e)}
