import json
from prompt import *
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
 
    def validate(self):
        result = {
            "questionId": self.question_id,
            "isCorrect": False,
            "status": 200
        }
        try:
            # MCQ validation
            if self.question_type_id == 1:
                self.is_correct = (self.user_answer == self.correct_answer)
                result["isCorrect"] = self.is_correct
            
            # Coding question validation
            elif self.question_type_id == 2:
                question_data = {
                    "questionid": self.question_id,
                    "question": self.correct_answer,
                    "user_answer": self.user_answer,
                    "constraints": self.constraints
                }
                
                response = json.loads(Prompt.check_coding(json.dumps(question_data)))
                
                if "error" in response:
                    return {
                        "questionId": self.question_id,
                        "error": response["error"],
                        "status": 400
                    }
                
                # Update attributes from response
                self.is_correct = response.get("isCorrect", False)
                self.feedback = response.get("feedback", "")
                self.hint = response.get("hint", "")
                # Update result
                result.update({
                    "isCorrect": self.is_correct,
                    "feedback": self.feedback,
                    "hint": self.hint
                })
                    
            # Fill-in-the-blank validation
            elif self.question_type_id == 3:
                question_data = {
                    "questionid": self.question_id,
                    "user_answer": self.user_answer,
                    "correct_answer": self.correct_answer
                }
                response = json.loads(Prompt.check_fill_in(json.dumps(question_data)))
                
                if "error" in response:
                    return {
                        "questionId": self.question_id,
                        "error": response["error"],
                        "status": 400
                    }
                
                self.is_correct = response.get("isCorrect", False)
                self.feedback = response.get("feedback", "")
                self.hint = response.get("hint", "")
                result.update({
                    "isCorrect": self.is_correct,
                    "feedback": self.feedback,
                    "hint": self.hint
                })

            # Drag-and-drop validation
            elif self.question_type_id == 4:
                self.is_correct = (self.user_answer == self.correct_answer)
                result["isCorrect"] = self.is_correct
                
            #error handling
            else:
                return {
                    "questionId": self.question_id,
                    "error": f"Unknown question type: {self.question_type_id}",
                    "status": 400
                }
                
        except Exception as e:
            return {
                "questionId": self.question_id,
                "error": f"Validation error: {str(e)}",
                "status": 500
            }
        return result
    
    def persist_answer(self):
        try:
            response = (
                supabase_client.table("Answer")
                .insert([{
                    "questionID": self.question_id,
                    "userID": self.user_id,
                    "userAnswer": self.user_answer,
                    "correctAnswer": self.correct_answer,
                    "correct": self.is_correct,
                    "feedback": self.feedback,
                    "hint": self.hint
                }])
                .execute()
            )
            return {"success": True, "data": response.data, "status": 201}
        
        except Exception as e:
            return {"success": False, "error": str(e), "status": 500}
    
    @classmethod
    def submit_answers(cls, user_id, answers_data):
        results = []
        
        for answer_data in answers_data:
            try:
                #create answer object
                answer = cls(
                    question_id=answer_data['questionId'],
                    user_id=user_id,
                    user_answer=str(answer_data['userAnswer']),
                    question_type_id=answer_data['questionTypeId'],
                    correct_answer=answer_data['correctAnswer'],
                    constraints=answer_data.get('constraints', '')
                )
                
                # Validate the answer
                validation_result = answer.validate()
                
                # Persist the answer
                persist_result = answer.persist_answer()
                
                # Combine results
                validation_result.update({
                    "persistenceSuccess": persist_result['success'],
                    "persistenceError": persist_result.get('error', '')
                })
                
                results.append(validation_result)
            
            except Exception as e:
                results.append({
                    "questionId": answer_data.get('questionId', 'unknown'),
                    "error": str(e),
                    "persistenceSuccess": False,
                    "status": 500
                })
        
        return results
        