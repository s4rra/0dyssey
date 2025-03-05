import base64
import os
import json
from flask import Flask, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
app = Flask(__name__)

def generate():
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    #test it and tell me what do you think about the output, if you have any notes inform me so i can edit the prompt
                    text="unit: loops, sub unit: for loops, skill level: intermediate"
                ),
            ],
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
                text="""Act as an energetic teacher generating Python questions in JSON format for students 10-17. Prioritize accurate JSON structure while maintaining an engaging tone. Unit and sub unit details will be specified for context of the questions.

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
  \"lesson\": \"\",
  \"chapter\": \"\",
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
        #print(chunk.text, end="")
        generated_text += chunk.text
        
    try:
        questions_json = json.loads(generated_text)
        return questions_json
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response"}

@app.route('/questions', methods=['Get'])
def get_questions():
    questions = generate()
    return jsonify(questions)

if __name__ == '__main__':
    app.run(debug=True)