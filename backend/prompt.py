import base64
import os
from google import genai
from google.genai import types

class Prompt: 
    
    @staticmethod   
    def generate_MCQ(prompt):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0.5,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["question", "options", "correct_answer", "tags", "avgTimeSeconds", "skillLevel"],
                        properties = {
                            "question": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "options": genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                required = ["a", "b", "c", "d"],
                                properties = {
                                    "a": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "b": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "c": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "d": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                },
                            ),
                            "correct_answer": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "tags": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                            "avgTimeSeconds": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                                description = "Estimated average time in seconds it would take a student to solve the question"
                            ),
                            "skillLevel": genai.types.Schema(
                                type = genai.types.Type.STRING,
                                enum = ["beginner", "intermediate", "advanced"],
                                description = "Target student skill level"
                            ),
                        },
                    ),
                ),
                system_instruction=[
                    types.Part.from_text(text="""Act as an energetic and engaging teacher creating 3 unique Python multiple-choice questions in a JSON array,
                                         each question must follow the schema exactly. Respond with a JSON array only. Make questions educational, age-appropriate (10–17),
                                         fun, and directly tied to the provided subunit description! Avoid repeating the same question with slight rewording
                                         A skill level: based on this user input: beginner = never coded, intermediate = some coding knowledge, advanced = knows other programming languages
                                         """),],
            )

            response = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text
            return response
        except Exception as e:
            return {
            "error": "Failed to generate MCQ",
            "details": str(e),
            "status": 500
        }
    
    @staticmethod
    def generate_coding(prompt):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0.5,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["question", "correct_answer", "constraints", "tags", "avgTimeSeconds", "skillLevel"],
                        properties = {
                            "question": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "correct_answer": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "constraints": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "tags": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                            "avgTimeSeconds": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                                description = "Estimated average time in seconds it would take a student to solve the question"
                            ),
                            "skillLevel": genai.types.Schema(
                                type = genai.types.Type.STRING,
                                enum = ["beginner", "intermediate", "advanced"],
                                description = "Target student skill level"
                            )
                        },
                    ),
                ),
                system_instruction=[
                    types.Part.from_text(text="""Act as an energetic and engaging teacher creating 4 Python short coding questions
                                         in a JSON array. Follow the schema exactly. Each question must ask the student to write code, not a full program.
                                         Stick to the subunit description content scope ONLY. Keep it educational, age-appropriate (10–17), and fun. 
                                         Avoid repeating the same question with slight rewording!
                                         A skill level: based on this user input: beginner = never coded, intermediate = some coding knowledge, advanced = knows other programming languages
                                         """),
                ],
            )

            response = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text
            return response
        except Exception as e:
            return {
            "error": "Failed to generate coding question",
            "details": str(e),
            "status": 500
        }
    
    @staticmethod     
    def generate_fill_in(prompt):
        try: 
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0.5,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["question", "correct_answer", "tags", "avgTimeSeconds", "skillLevel"],
                        properties = {
                            "question": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "correct_answer": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "tags": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                            "avgTimeSeconds": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                                description = "Estimated average time in seconds it would take a student to solve the question"
                            ),
                            "skillLevel": genai.types.Schema(
                                type = genai.types.Type.STRING,
                                enum = ["beginner", "intermediate", "advanced"],
                                description = "Target student skill level"
                            )
                        },
                    ),
                ),
                system_instruction=[
                    types.Part.from_text(text="""Act as an energetic and engaging Python teacher creating 2 unique fill-in-the-blank questions in a JSON array.
                                    Each question must:
                                    Be directly based on the given subunit description.
                                    Be age-appropriate (10–17).
                                    Contain 1 or 2 blanks, marked clearly as _____.
                                    Include a correct_answer array matching the blanks in order.
                                    Strictly follow the structured schema provided.
                                    Keep the questions clear, relevant, and educational. Avoid repeating concepts or introducing topics outside the subunit’s scope
                                    A skill level: based on this user input: beginner = never coded, intermediate = some coding knowledge, advanced = knows other programming languages
                                    """),
                        ],
                    )

            response = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text
            return response
        
        except Exception as e:
            return {
            "error": "Failed to generate fill in the blanks",
            "details": str(e),
            "status": 500
            }
    
    @staticmethod
    def generate_drag_and_drop(prompt):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0.5,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["question", "correct_answer", "options", "tags",  "avgTimeSeconds", "skillLevel"],
                        properties = {
                            "question": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "correct_answer": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                            "options": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                            "tags": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                            "avgTimeSeconds": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                                description = "Estimated average time in seconds it would take a student to solve the question"
                            ),
                            "skillLevel": genai.types.Schema(
                                type = genai.types.Type.STRING,
                                enum = ["beginner", "intermediate", "advanced"],
                                description = "Target student skill level"
                            ),
                        },
                    ),
                ),
                system_instruction=[
                    types.Part.from_text(text="""Act as an engaging Python instructor. Generate 2 unique drag-and-drop Python questions in a JSON array.
                                        Each question must:
                                        - Be clearly tied to the provided subunit description
                                        - Include stricktly 2 to 3 blanks in the code or question to be filled in (use `_____`), or include blanks at the end of the question if the question asks to "Drag the correct blocks into the blanks"
                                        - Be age-appropriate (10–17), fun, and educational
                                        - Include a `question` (context with blanks), `correct_answer` (ordered list), and `options` (correct answers + distractors)
                                        - Follow the JSON schema exactly

                                        Do NOT repeat the same pattern, and don’t go beyond the subunit scope.
                                        A skill level: based on this user input: beginner = never coded, intermediate = some coding knowledge, advanced = knows other programming languages
                                        """),
                ],
            )

            response = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text
            return response    
        except Exception as e:
            return {
            "error": "Failed to generate drag and drop",
            "details": str(e),
            "status": 500
            }  
    
    @staticmethod
    def check_coding(input_data):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text = input_data),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0.2,
                top_p=1,
                top_k=40,
                max_output_tokens=500,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["questionid", "user_answer", "hint", "feedback", "isCorrect", "points"],
                    properties = {
                        "questionid": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "ID that links this feedback to the original question",
                        ),
                        "user_answer": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "The student's submitted code or answer",
                        ),
                        "hint": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "A Socratic-style hint that nudges the student to think deeper without revealing the answer",
                        ),
                        "feedback": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "Encouraging, constructive feedback, NO suggestions",
                        ),
                        "isCorrect": genai.types.Schema(
                            type = genai.types.Type.BOOLEAN,
                            description = "True if the user's answer logically solves the question as written. False otherwise, user’s answers is actually correct and logical to question needs",
                        ),
                        "points": genai.types.Schema(
                            type = genai.types.Type.NUMBER,
                            description = "Score out of 10 based on how well the student's code meets the question's requirements",
                        ),
                    },
                ),
                system_instruction=[
                    types.Part.from_text(text="""You are a Python tutor analyzing a student's answer to a coding question.
                            Determine if the student's code logically solves the problem described or stated in the "question" field fully.
                            Do NOT compare to "correct_answer" literally. Instead, judge whether the code accomplishes what the question ASKS FOR.
                            user answer should match "constraints", if it doesnt, the user answer is incorrect.

                            If the solution is CORRECT:
                            feedback: Give brief, positive reinforcement only (e.g. “Well done!” or “Correct.”) and briefly explain the users currect answer.
                            hint: Provide a deeper-thinking challenge (e.g. “now, what if the input was a float instead of an integer?”).
                            If the solution is INCORRECT:
                            user answer doesnt apply the "constraints".
                            user answer doesnt ful fill the question text or needs.
                            feedback: State only what the user current code does (e.g. “thats not quite right, your code does ...”) Socratic-style, no.
                            hint: Use a Socratic-style question that nudges the student to figure out what went wrong, without revealing the solution (e.g. “How do we usually get input from the user?”).

                            NEVER:
                            Do NOT give direct suggestions or code in feedback or hint.
                            Do NOT reveal the correct answer.
                            Do NOT praise incorrect answers.
                            
                            based on time taken to solve in seconds compared to avgTimeSeconds , give score out of 10 in points
                            If no answer is submitted for a question, assume it's incorrect and provide feedback and a hint that explain the correct approach or concept behind the question
                            """),
                            ],
                        )

            response = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text
            return response
        except Exception as e:
            return {
            "error": "Failed to analyze user's coding answer",
            "details": str(e),
            "status": 500
        }
       
    @staticmethod
    def check_fill_in(input_data):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text = input_data),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0.2,
                top_p=1,
                top_k=40,
                max_output_tokens=500,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["questionid", "user_answer", "isCorrect", "hint", "feedback","points"],
                    properties = {
                        "questionid": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "ID to link this analysis to the original question",
                        ),
                        "user_answer": genai.types.Schema(
                            type = genai.types.Type.ARRAY,
                            description = "Array of user-provided answers",
                            items = genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                        ),
                        "isCorrect": genai.types.Schema(
                            type = genai.types.Type.BOOLEAN,
                            description = "True if the user’s answers is actually correct and logical to question needs",
                        ),
                        "hint": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "Socratic-style hint guiding student thinking without giving the answer",
                        ),
                        "feedback": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "Constructive yet encouraging comment, No suggestions",
                        ),
                        "points": genai.types.Schema(
                            type = genai.types.Type.INTEGER,
                            description = "Score out of 8 based on how well the student's code meets the question's requirements"
                        ),
                    },
                ),
                system_instruction=[
                    types.Part.from_text(text="""You are a Python tutor helping assess student answers for fill-in-the-blank Python questions. These questions may contain 1 to 3 blanks, marked as \"_____\".

                        Your job is to evaluate if the student's answers fill the blanks logically and correctly, based on the context of the original question.

                        You MUST:
                        - Use the original question as the main reference (not the exact correct answer).
                        - Accept alternate correct phrasing or synonyms if they make sense.
                        - Use the expected answers (correct_answer) as a guide, not a strict match.
                        - If the student answer is logically correct, mark it as correct (correct!, great work!).
                        - user answer is incorrect doesnt full fill the question text or needs.
                        - for hints, use a short Socratic-style hint (that encourages thinking without giving the answer).
                        - Keep all feedback short, Socratic-style and focused, (not quite right, your code does...), Do NOT give away the correct answer, do not give tips or suggestions
                        
                        based on time taken to solve in seconds compared to avgTimeSeconds , give score out of 7 in points
                        
                        Your response MUST follow this exact JSON schema
                        If no answer is submitted for a question, assume it's incorrect and provide feedback and a hint that explain the correct approach or concept behind the question"""),
                                ],
                            )

            response = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text
            return response
        
        except Exception as e:
            return {
            "error": "failed to analyze user's fill in the blanks answer",
            "details": str(e),
            "status": 500
        }
    
    @staticmethod
    def check_performance(data):
        try:   
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=data),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0,
                top_p=1,
                top_k=40,
                max_output_tokens=300,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                required = ["levelSuggestion", "aiSummary", "feedbackPrompt","tagInsights"],
                                properties = {
                                    "levelSuggestion": genai.types.Schema(
                                        type = genai.types.Type.INTEGER,
                                        description = "Recommended skill level is (1 = Beginner, 2 = Intermediate, 3 = Advanced)",
                                    ),
                                    "aiSummary": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                        description = "summary of user performance. Analyze tagPerformance to identify specific topic weaknesses. ",
                                    ),
                                    "feedbackPrompt": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                        description = "teacher message to show the user as a popup when a level change is suggested",
                                    ),
                                    "tagInsights": genai.types.Schema(
                                        type = genai.types.Type.ARRAY,
                                        description = "Top tags where the user did well",
                                        items = genai.types.Schema(
                                            type = genai.types.Type.OBJECT,
                                            properties = {
                                                "tag": genai.types.Schema(
                                                    type = genai.types.Type.STRING,
                                                    description = "Name of the top 5 tags. top tag=high percentage and high total"
                                                ),
                                                "percentage": genai.types.Schema(
                                                    type = genai.types.Type.NUMBER,
                                                    description = "percentage of the top 5 tags. top tag=high percentage and high total"
                                                )
                                            },
                                            required = ["tag", "percentage"]
                                        )
                                    )

                                },
                            ),
                system_instruction=[
                    types.Part.from_text(text="""
                                         You are a Python teacher reviewing the progress of students aged 10–17.
                            Based on their lesson-level performance (subunits), generate the following:
                            - aiSummary: A **short**, motivational message (1–3 sentences max) with personalized guidance. Write as if you are giving quick feedback to a student. Avoid long paragraphs or overly generic advice.
                            Example: “Great job with logical operators! You’re ready to try more advanced problems.”
                            - levelSuggestion: Suggest a new skill level as a number (1, 2, or 3).
                            - feedbackPrompt: A popup-style message if a level change is recommended.
                            Examples: “Do you want to change to level 2?”, “I think you’re ready for level 3.”, “I suggest you stay at level 1.”
                            - tagInsights: Pick the top 5 tags from tagPerformance.
                            Prioritize:
                            - Tags with highest correctness percentage
                            - Tags with highest total attempts
                            When analyzing performance, consider:
                            - Correct answers vs. total questions
                            - Time taken compared to average solving time
                            - Trends across multiple lessons (subunits)
                            - The user’s current skill level
                            - Tag-level performance to highlight strengths and weaknesses
                            """),
                ],
            )

            response = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text
            return response
        except Exception as e:
            return {
            "error": "failed to analyze user's performance",
            "details": str(e),
            "status": 500
        }
    