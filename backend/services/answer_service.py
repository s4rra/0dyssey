import base64
import os
import json
from google import genai
from google.genai import types
from config.settings import supabase_client
from services.user_service import *
from services.question_service import *

class Answer:
    def __init__(self, 
                 question_id: int, 
                 user_id: int, 
                 user_answer: str, 
                 question_type_id: int, 
                 correct_answer: str,
                 constraints: str = None):
        self.question_id = question_id
        self.user_id = user_id
        self.user_answer = user_answer
        self.question_type_id = question_type_id
        self.correct_answer = correct_answer
        self.constraints = constraints
        self.is_correct = False
        self.feedback = None
        self.hint = None

    def check_coding(input):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=input),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0,
                top_p=1,
                top_k=40,
                max_output_tokens=500,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["questionid", "user_answer", "hint", "feedback"],
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
                            description = "Encouraging, constructive feedback with high-level suggestions or questions",
                        ),
                    },
                ),
                system_instruction=[
                    types.Part.from_text(text="""You are a Python tutor analyzing student answers for multiple Python coding questions for students aged 10–17.
                    Your task is to:
                    Compare the user’s answer with the expected output and any provided constraints
                    Identify errors: Highlight syntax mistakes, logic errors, or violations of the constraints
                    Provide hints: Offer a Socratic-style hint that points out where the issue may lie, without revealing the solution. Avoid naming specific functions or methods
                    Analyze efficiency: Comment on whether the solution could be improved (if applicable)
                    Give feedback: Encourage correct answers with reinforcement, and provide constructive feedback if incorrect by guiding the student toward discovery using a relatable example or question
                    Your response must follow the structured output format and stay within the scope of the student’s input.
                    expected input:
                    {
                    \"questionid\": \"\",
                    \"question\": \"\",
                    \"correct_answer\": \"expected output\",
                    \"constraints\": \"\",
                    \"user_answer\": \"\"
                    }"""),
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
            "error": "Failed to analyze student's coding answer",
            "details": str(e),
            "status": 500
        }
       
    def validate(self):
        # MCQ validation
        if self.question_type_id == 1:
            self.is_correct = (self.user_answer == self.correct_answer)
            return {
                "questionId": self.question_id,
                "isCorrect": self.is_correct
            }
        
        # Coding question validation
        elif self.question_type_id == 2:
            # Prepare input for check_coding method
            input_data = json.dumps({
                "questionid": str(self.question_id),
                "question": "",  # We might want to fetch this from the database
                "correct_answer": self.correct_answer,
                "constraints": self.constraints or "",
                "user_answer": self.user_answer
            })
            
            # Call check_coding to get feedback
            result = Answer.check_coding(input_data)
            
            try:
                # Parse the result
                parsed_result = json.loads(result)
                self.hint = parsed_result.get('hint', '')
                self.feedback = parsed_result.get('feedback', '')
                
                # For now, we'll set it to False
                self.is_correct = False
                
                return {
                    "questionId": self.question_id,
                    "hint": self.hint,
                    "feedback": self.feedback,
                    "isCorrect": self.is_correct
                }
            except Exception as e:
                return {
                    "questionId": self.question_id,
                    "error": f"Failed to process coding answer: {str(e)}"
                }

    def persistAns(self):
        try:
            # Persist answer to the database
            response = (
                supabase_client.table("UserAnswer")
                .insert([
                    {
                        "questionID": self.question_id,
                        "userID": self.user_id,
                        "userAnswer": self.user_answer,
                        "isCorrect": self.is_correct,
                        "feedback": self.feedback,
                        "hint": self.hint
                    }
                ])
                .execute()
            )
            return {"success": True, "data": response.data}
        except Exception as exception:
            return {"success": False, "error": str(exception), "status": 500}

    @classmethod
    def submit_answers(cls, user_id, answers_data):
        results = []
        
        for answer_data in answers_data:
            try:
                answer = cls(
                    question_id=answer_data['questionId'],
                    user_id=user_id,
                    user_answer=answer_data['userAnswer'],
                    question_type_id=answer_data['questionTypeId'],
                    correct_answer=answer_data['correctAnswer'],
                    constraints=answer_data.get('constraints', '')
                )
                
                # Validate the answer
                validation_result = answer.validate()
                
                # Persist the answer
                persist_result = answer.persistAns()
                
                # Combine validation and persistence results
                result = {
                    **validation_result,
                    "persistenceSuccess": persist_result['success']
                }
                
                results.append(result)
            
            except Exception as e:
                results.append({
                    "questionId": answer_data['questionId'],
                    "error": str(e)
                })
        
        return results