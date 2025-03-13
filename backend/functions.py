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

Guidelines:
Randomize the order of all questions options. The correct answer should not consistently appear in the same position (e.g., "a").
Ensure coding questions are precise and well-defined, providing clear instructions.
Utilize placeholders like "[BLANK_1]" , "[BLANK_2]" , etc., within the question text to indicate dropdown locations.
Fill-in-the-Blanks Questions:
Represent blanks with underscores (_____).
Allow for 1 or 2 blanks per question.
Provide answer options that contain the completed blanks.
Do not use "[BLANK]" placeholders for fill in the blank questions.
Avoid using single quotes (') or double quotes (") in the question text, except for code formatting purposes.

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

def check_code():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.5,
        top_k=40,
        max_output_tokens=500,
        response_mime_type="application/json",
        system_instruction=[
            types.Part.from_text(text="""You are a Python tutor analyzing student answers for multiple Python coding questions for students aged 10-17. Your task is to:

Check correctness: Compare the user’s answer with the expected output and constraints.
Identify errors: Highlight syntax mistakes, logic errors, or constraint violations.
Provide hints: Offer a logical hint that points out the issue without revealing the solution. Do not suggest specific functions or methods.
Analyze efficiency: Comment on whether the solution can be improved.
Give feedback: Encourage correct answers, and provide constructive feedback if incorrect by giving an example similar to the question..
Input Format json object, for each question:
{
  \"type\": \"coding\",
  \"question\": \"\",
  \"expected_output\": \"\",
  \"constraints\": \"\",
  \"user_answer\": \"\"
}
output Format json object, for each question:
{
  \"type\": \"check\",
  \"question\": \"\",
  \"user_answer\": \"\",
  \"hints\": \"Logical hints pointing out the issue.\",
  \"feedback\": \"Encouragement if correct, constructive feedback if incorrect.\"
}"""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")
