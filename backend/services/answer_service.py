import base64
import os
import json
from google import genai
from google.genai import types
from config.settings import supabase_client

class Answer:
    def __init__(self, question_id, user_id, user_answer, correct_answer, question_type_id, constraints=""):
        self.question_id = question_id
        self.user_id = user_id
        self.user_answer = user_answer
        self.correct_answer = correct_answer
        self.question_type_id = question_type_id 
        self.constraints = constraints           
        self.is_correct = None
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
                temperature=0.2,
                top_p=1,
                top_k=40,
                max_output_tokens=500,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["questionid", "user_answer", "hint", "feedback", "isCorrect"],
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
                            description = "Encouraging, constructive feedback with high-level observations, not suggestions",
                        ),
                        "isCorrect": genai.types.Schema(
                            type = genai.types.Type.BOOLEAN,
                            description = "True if the user's answer logically solves the question as written. False otherwise",
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
                            feedback: State only what the user current code does (e.g. “thats not quite right, your code does ...”).
                            hint: Use a Socratic-style question that nudges the student to figure out what went wrong, without revealing the solution (e.g. “How do we usually get input from the user?”).

                            NEVER:
                            Do NOT give direct suggestions or code in feedback or hint.
                            Do NOT reveal the correct answer.
                            Do NOT praise incorrect answers."""),
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
            input_data = {
                "questionid": self.question_id,
                "question": self.correct_answer,
                "user_answer": self.user_answer,
                "constraints": self.constraints
            }
            
            response = Answer.check_coding(json.dumps(input_data))
            
            try:
                result = json.loads(response)
                
                # Check if there was an error in the response
                if "error" in result:
                    return {
                        "questionId": self.question_id,
                        "isCorrect": False,
                        "error": result["error"]
                    }
                
                # Set the feedback and hint from the response
                self.feedback = result.get("feedback", "")
                self.hint = result.get("hint", "")
                
                # Set whether the answer is correct
                self.is_correct = result.get("isCorrect", False)
                
                return {
                    "questionId": self.question_id,
                    "isCorrect": self.is_correct,
                    "feedback": self.feedback,
                    "hint": self.hint
                }
            except Exception as e:
                # Handle JSON parsing errors or other exceptions
                self.is_correct = False
                return {
                    "questionId": self.question_id,
                    "isCorrect": False,
                    "error": f"Failed to process response: {str(e)}"
                }
        
        # Handle other question types for now
        else:
            return {
                "questionId": self.question_id,
                "isCorrect": False,
                "error": f"Unknown question type: {self.question_type_id}"
            }

    def persistAns(self):
        try:
            # Persist answer to the database
            print("Saving answer for question:", self.question_id)
            response = (
                supabase_client.table("Answer")
                .insert([
                    {
                        "questionID": self.question_id,
                        "userID": self.user_id,
                        "userAnswer": self.user_answer,
                        "correctAnswer": self.correct_answer,
                        "correct": self.is_correct,
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
                    user_answer=str(answer_data['userAnswer']),  # Ensure string conversion
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
                    "persistenceSuccess": persist_result['success'],
                    "persistenceError": persist_result.get('error', '')
                }
                
                results.append(result)
            
            except Exception as e:
                results.append({
                    "questionId": answer_data['questionId'],
                    "error": str(e),
                    "persistenceSuccess": False
                })
        
        return results
        