from datetime import datetime
import json 
from prompt import Prompt 
from config.settings import supabase_client 

#utility class
class ScoreCalculator:
    BASE_POINTS = {
        1: 5,  # MCQ
        4: 8   # Drag-drop
    }
    
    SKILL_BONUS = {
        1: 1,
        2: 2,
        3: 3
    }

    @staticmethod
    def apply_bonuses(base_score, is_correct, retry, time_taken, avg_time, skill_level):
        if not is_correct:
            return 0

        skill_bonus = ScoreCalculator.SKILL_BONUS.get(skill_level, 0)
        retry_penalty = retry
        time_bonus = 4 if time_taken < avg_time else 0

        total = base_score + skill_bonus + time_bonus - retry_penalty
        return max(0,total)
    
    @staticmethod
    def deduct_for_hint(user_id):
        try:
            res = supabase_client.table("User") \
            .select("points") \
            .eq("userID", user_id) \
            .single() \
            .execute()

            current_points = res.data["points"]
            
            if current_points < 29:
                return {
                    "success": False,
                    "message": f"Not enough points to use a hint. You have {current_points} points!"
                }

            new_points = current_points - 30

            supabase_client.table("User") \
            .update({"points": new_points}) \
            .eq("userID", user_id) \
            .execute()

            return {"success": True, "updatedPoints": new_points}
        except Exception as e:
            return {"error": str(e)}

class AnswerModel:
    def __init__(self, answer_data, user_id, skill_level=None):
        if isinstance(answer_data, str):
            answer_data = json.loads(answer_data)
        
        self.user_id = user_id
        self.question_id = answer_data["questionId"]
        self.question_type_id = answer_data.get("questionTypeId")
        self.user_answer = answer_data.get("userAnswer", "")
        self.start_time = datetime.fromtimestamp(answer_data.get("startTime"))
        self.end_time = datetime.fromtimestamp(answer_data.get("endTime"))
        self.skill_level = skill_level
        delta = self.end_time - self.start_time
        self.time_taken = max(1, int(delta.total_seconds()))

        self.question_text = ""
        self.correct_answer = ""
        self.constraints = ""
        self.avg_time = 90

        self.is_correct = False
        self.points = 0
        self.feedback = ""
        self.hint = ""
        self.retry = self.get_retry_count()

        self.load_question()
    
    def validate(self):
        if self.question_type_id in (1, 4):
            self.is_correct = self.user_answer == self.correct_answer
            base_score = ScoreCalculator.BASE_POINTS[self.question_type_id]
            self.points = ScoreCalculator.apply_bonuses(
                base_score=base_score,
                is_correct=self.is_correct,
                retry=self.retry,
                time_taken=self.time_taken,
                avg_time=self.avg_time,
                skill_level=self.skill_level
            )
            return

        if self.question_type_id == 2:
            payload = {
                "questionid": self.question_id,
                "question": self.question_text,
                "user_answer": self.user_answer,
                "constraints": self.constraints,
                "avgTimeSeconds": self.avg_time,
                "timeTaken": self.time_taken
            }
            raw_response = Prompt.check_coding(json.dumps(payload))

        elif self.question_type_id == 3:
            parsed_answer = self.correct_answer
            payload = {
                "questionid": self.question_id,
                "user_answer": self.user_answer,
                "correct_answer": parsed_answer,
                "avgTimeSeconds": self.avg_time,
                "timeTaken": self.time_taken
            }
            raw_response = Prompt.check_fill_in(json.dumps(payload))

        else:
            raise Exception("Unsupported question type")
        
        response = json.loads(raw_response) if isinstance(raw_response, str) else raw_response

        if "error" in response:
            raise Exception(response["error"])

        self.is_correct = response.get("isCorrect", False)
        self.feedback = response.get("feedback", "")
        self.hint = response.get("hint", "")
        self.points = ScoreCalculator.apply_bonuses(
            base_score=int(response.get("points", 0)),
            is_correct=self.is_correct,
            retry=self.retry,
            time_taken=self.time_taken,
            avg_time=self.avg_time,
            skill_level=self.skill_level
        )
        
    def persist(self):
        try:
            res = supabase_client.table("Answer") \
                .select("answerID") \
                .eq("userID", self.user_id) \
                .eq("questionID", self.question_id) \
                .maybe_single() \
                .execute()
                
            existing = res.data if res and hasattr(res, "data") else None

            payload = {
                "questionID": self.question_id,
                "userID": self.user_id,
                "userAnswer": self.user_answer,
                "correctAnswer": self.correct_answer,
                "is_correct": self.is_correct,
                "feedback": self.feedback if self.question_type_id in (2, 3) else "",
                "hint": self.hint if self.question_type_id in (2, 3) else "",
                "Points": self.points,
                "retry": self.retry,
                "startedAt": self.start_time.isoformat(),
                "completedAt": self.end_time.isoformat(),
                "timeTaken": self.time_taken 
            }
            
            print("\nANSWER ANALYSIS IN TERMINAL -----------------------")
            print(f"QuestionID    : {self.question_id}")
            print(f"UserID        : {self.user_id}")
            print(f"Skill Level   : {self.skill_level}")
            print(f"Retries       : {self.retry}")
            print(f"AvgTime       : {self.avg_time} seconds")
            print(f"Time Taken    : {self.time_taken} seconds")
            print(f"Is Correct     : {self.is_correct}")
            print(f"Points Earned : {self.points}")
            print("----------------------------------------------------\n")

            if existing:
                supabase_client.table("Answer") \
                    .update(payload, count="exact") \
                    .eq("answerID", existing["answerID"]) \
                    .execute()
            else:
                payload["retry"] = 0
                supabase_client.table("Answer") \
                    .insert([payload], count="exact") \
                    .execute()

        except Exception as e:
            raise Exception("db save failed: " + str(e))
    
    def get_retry_count(self):
        try:
            res = supabase_client.table("Answer") \
                .select("retry") \
                .eq("userID", self.user_id) \
                .eq("questionID", self.question_id) \
                .maybe_single() \
                .execute()
            data = res.data
            if data:
                return data.get("retry", 0) + 1
            return 0
        except Exception:
            return 0

    def load_question(self):
        try:
            res = supabase_client.table("Question") \
                .select("questionText", "correctAnswer", "constraints", "avgTimeSeconds") \
                .eq("questionID", self.question_id) \
                .single() \
                .execute()
            q = res.data
            
            self.question_text = q.get("questionText", "")
            self.correct_answer = q.get("correctAnswer", "")
            self.constraints = q.get("constraints", "")
            self.avg_time = q.get("avgTimeSeconds", 90)
            
            if isinstance(self.correct_answer, str):
                try:
                    self.correct_answer = json.loads(self.correct_answer)
                except json.JSONDecodeError:
                    pass
                    
            if isinstance(self.constraints, str):
                try:
                    self.constraints = json.loads(self.constraints)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            raise Exception("Failed to load question info: " + str(e))

class AnswerService:
    @staticmethod
    def submit_answers(user_id, answers_data, skill_level):
        try:
            if isinstance(answers_data, str):
                answers_data = json.loads(answers_data)
        except json.JSONDecodeError:
            return {"results": [], "error": "Invalid JSON input"}

        total_points = 0
        results = []

        for a in answers_data:
            if isinstance(a, str):
                try:
                    a = json.loads(a)
                except Exception as e:
                    return {"results": [], "error": f"Failed to parse entry: {str(e)}"}

            try:
                ans = Answer(a, user_id, skill_level)
                ans.validate()
                ans.persist()
                total_points += ans.points
                results.append({
                    "questionId": ans.question_id,
                    "success": True,
                    "isCorrect": ans.is_correct,
                    "points": ans.points,
                    "feedback": ans.feedback,
                    "hint": ans.hint,
                    "retry": ans.retry
                })
            except Exception as e:
                results.append({
                    "questionId": a.get("questionId", "unknown") if isinstance(a, dict) else "unknown",
                    "success": False,
                    "error": str(e)
                })

        try:
            res = supabase_client.table("User") \
                .select("points") \
                .eq("userID", user_id) \
                .single() \
                .execute()
            user_data = res.data

            old_points = user_data.get("points", 0)
            new_total = old_points + total_points
            supabase_client.table("User") \
                .update({"points": new_total}) \
                .eq("userID", user_id) \
                .execute()
        except Exception as e:
            results.append({"error": "Failed to update user points: " + str(e)})

        return {"results": results}
    