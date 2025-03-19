import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
#uses  google gemini API to generate questions
def generate_questions(subunit_description, skill_level):
    #Returns:list: A list of generated questions in JSON format.
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    
    # User input (formatted as JSON for clarity)
    user_prompt = json.dumps({
        "subunit": subunit_description,
        "skill_level": skill_level
    })

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
        response_mime_type="application/json",  # Ensure JSON output
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            required=["questions"],
            properties={
                "questions": genai.types.Schema(
                    type=genai.types.Type.ARRAY,
                    items=genai.types.Schema(
                        type=genai.types.Type.OBJECT,
                        required=["type", "question"],
                        properties={
                            "type": genai.types.Schema(
                                type=genai.types.Type.STRING,
                                description="The type of question: Multiple Choice, Fill-in-the-Blanks, DropDown, or Coding.",
                                enum=["fill_in_the_blanks", "MCQ", "DropDown", "coding"],
                            ),
                            "question": genai.types.Schema(
                                type=genai.types.Type.STRING,
                                description="The question text, formatted according to its type.",
                            ),
                            "options": genai.types.Schema(
                                type=genai.types.Type.OBJECT,
                                description="The answer choices for MCQ and Fill-in-the-Blanks questions.",
                                nullable=True,
                                properties={
                                    "a": genai.types.Schema(type=genai.types.Type.STRING),
                                    "b": genai.types.Schema(type=genai.types.Type.STRING),
                                    "c": genai.types.Schema(type=genai.types.Type.STRING),
                                    "d": genai.types.Schema(type=genai.types.Type.STRING),
                                },
                            ),
                            "correct_answer": genai.types.Schema(
                                type=genai.types.Type.STRING,
                                description="Correct answer(s). For MCQs and Fill-in-the-Blanks, this is 'a', 'b', 'c', or 'd'.",
                                nullable=True,
                            ),
                            "dropdowns": genai.types.Schema(
                                type=genai.types.Type.ARRAY,
                                description="Only applicable to DropDown question type.",
                                nullable=True,
                                items=genai.types.Schema(
                                    type=genai.types.Type.OBJECT,
                                    properties={
                                        "placeholder": genai.types.Schema(
                                            type=genai.types.Type.STRING,
                                            description="The placeholder in the question text (e.g., '[BLANK_1]').",
                                        ),
                                        "options": genai.types.Schema(
                                            type=genai.types.Type.ARRAY,
                                            items=genai.types.Schema(type=genai.types.Type.STRING),
                                        ),
                                        "correctAnswer": genai.types.Schema(
                                            type=genai.types.Type.STRING,
                                            description="The correct answer from the dropdown options.",
                                        ),
                                    },
                                ),
                            ),
                            "expected_output": genai.types.Schema(
                                type=genai.types.Type.STRING,
                                description="The expected output for coding questions.",
                                nullable=True,
                            ),
                            "constraints": genai.types.Schema(
                                type=genai.types.Type.STRING,
                                description="Any constraints or conditions the user should follow for coding questions.",
                                nullable=True,
                            ),
                        },
                    ),
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(text="""
                Act as an energetic teacher generating Python questions for students aged 10-17.
                Your goal is to create new engaging and structured questions based on the given 
                subunit and skill level.

                Skill Levels & Allowed Question Types:
                - Beginner: fill_in_the_blanks, DropDown, MCQ (5 questions)
                - Intermediate: fill_in_the_blanks, DropDown, MCQ, coding Questions (5 questions)
                - Advanced: coding Questions only (5 questions)

                Guidelines:
                - Randomize all question options.
                - Fill-in-the-blanks: Use underscores (___) instead of placeholders.
                - DropDown Questions: Use placeholders like "[BLANK_1]", "[BLANK_2]" in the question text.
                - Ensure coding questions have clear constraints and an expected output.
                - Avoid single quotes (') or double quotes (") in question text, except for code formatting.
                - Questions must be directly related to the subunit.

                Response Constraints
                The AI must generate questions in JSON format according to the provided schema.
            """),
        ],
    )

    # Keep Streaming from Google AI Studio but Collect JSON Response
    generated_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        generated_text += chunk.text  # Keep collecting the streamed response

    try:
        questions_json = json.loads(generated_text)
        return questions_json["questions"]
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response"}

#uses google gemini API to evaluate user code...needs review
def check_code(user_code, expected_output, constraints):
    input_data = {
        "type": "coding",
        "question": "Code evaluation",
        "expected_output": expected_output,
        "constraints": constraints,
        "user_answer": user_code
    }
    
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[ types.Part.from_text(text=json.dumps(input_data)) ],
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

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text
        
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response"}
