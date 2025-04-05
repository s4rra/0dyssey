import json
from prompt import *
from services.rewards import *
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
        self.retry = 0  # Default until retry support is added
        self.time_taken = None  # Placeholder
        self.skill_level = None  # Will be passed in from submit_answers
        self.points = 0
 
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
                if not self.is_correct:
                    self.feedback = "Not quite right. Try re-reading the question and eliminate obvious wrong answers."
                    self.hint = "Think about how Python handles this concept. Is there a keyword or structure being overlooked?"

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
                if not self.is_correct:
                    self.feedback = "Not quite right. Try re-reading the question and eliminate obvious wrong answers."
                    self.hint = "Think about how Python handles this concept. Is there a keyword or structure being overlooked?"

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
    
    def set_evaluation(self, result_data, time_taken, retry, skill_level):
        self.is_correct = result_data.get("isCorrect", False)
        self.feedback = result_data.get("feedback", "")
        self.hint = result_data.get("hint", "")
        self.time_taken = time_taken
        self.retry = Answer.get_retry_count(self.user_id, self.question_id) + 1

        # Call reward system
        # Fetch avgTimeSeconds from Question table
        try:
            q_data = supabase_client.table("Question").select("avgTimeSeconds").eq("questionID", self.question_id).single().execute()

            avg_time = q_data.data.get("avgTimeSeconds", 120)  # fallback to 120s if missing

        except Exception as e:
            avg_time = 120  # default fallback
            print(f"[Warning] Failed to fetch avg time for question {self.question_id}: {e}")

        # Call reward system
        from services.rewards import RewardSystem
        self.points = RewardSystem.calculate_points(
            question_type_id=self.question_type_id,
            is_correct=self.is_correct,
            retry=self.retry,
            time_taken=self.time_taken,
            skill_level=skill_level,
            avg_time=avg_time
        )

    def persist_answer(self):
        try:
            # Check if answer already exists
            existing = (
                supabase_client.table("Answer")
                .select("answerID")
                .eq("userID", self.user_id)
                .eq("questionID", self.question_id)
                .single()
                .execute()
            )

            if existing.data:
                # Update existing answer
                response = (
                    supabase_client.table("Answer")
                    .update({
                        "userAnswer": self.user_answer,
                        "correctAnswer": self.correct_answer,
                        "correct": self.is_correct,
                        "feedback": self.feedback,
                        "hint": self.hint,
                        "points": self.points,
                        "retry": self.retry,
                        "timeTakenSeconds": self.time_taken
                    })
                    .eq("answerID", existing.data["answerID"])
                    .execute()
                )
            else:
                # Insert new answer
                response = (
                    supabase_client.table("Answer")
                    .insert([{
                        "questionID": self.question_id,
                        "userID": self.user_id,
                        "userAnswer": self.user_answer,
                        "correctAnswer": self.correct_answer,
                        "correct": self.is_correct,
                        "feedback": self.feedback,
                        "hint": self.hint,
                        "points": self.points,
                        "retry": self.retry,
                        "timeTakenSeconds": self.time_taken
                    }])
                    .execute()
                )

            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e), "status": 500}

    @staticmethod
    def get_retry_count(user_id, question_id):
        try:
            response = (
                supabase_client.table("Answer")
                .select("retry")
                .eq("userID", user_id)
                .eq("questionID", question_id)
                .maybe_single()
                .execute()
            )
            if response.data:
                return response.data.get("retry", 0)
            return 0
        except Exception as e:
            print("Retry fetch error:", str(e))
            return 0

    @staticmethod
    def calculate_time_taken(start_time):
        from datetime import datetime
        try:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            return int(duration)
        except Exception as e:
            print("Time tracking error:", str(e))
            return 60  # fallback

    @classmethod
    def submit_answers(cls, user_id, answers_data, skill_level):
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
                
                # Use placeholders for retry/time (real values can be injected later)
                answer.set_evaluation(
                    result_data=validation_result,
                    time_taken=answer_data.get('timeTaken', 60),
                    retry=answer_data.get('retry', 0),
                    skill_level=skill_level
                )

                persist_result = answer.persist_answer()
                
                # Combine results
                validation_result.update({
                    "pointsAwarded": answer.points,
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
        