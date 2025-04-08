import json
from prompt import Prompt
from config.settings import supabase_client
from datetime import datetime
from services.user_service import *

class ScoreCalculator:
    BASE_POINTS = {
        1: 5,  # MCQ
        4: 8   # Drag-drop
    }

    SKILL_BONUS = {
        1: 1,  # Beginner
        2: 2,  # Intermediate
        3: 3   # Advanced
    }

    @staticmethod
    def calculate_points(question_type_id, is_correct, retry, time_taken, skill_level, avg_time, base_score=None):
        if not is_correct:
            return 0

        base = base_score if base_score is not None else ScoreCalculator.BASE_POINTS.get(question_type_id, 0)
        skill_bonus = ScoreCalculator.SKILL_BONUS.get(skill_level, 0)
        retry_penalty = max(0, retry - 1)

        time_bonus = 0
        if time_taken is not None and avg_time:
            if time_taken < avg_time * 0.5:
                time_bonus = 3
            elif time_taken < avg_time * 0.75:
                time_bonus = 2
            elif time_taken < avg_time:
                time_bonus = 1

        total = base + skill_bonus + time_bonus - retry_penalty
        return max(total, 1)

class Answer:
    def __init__( answer_data, user_id, skill_level=None):
        self.question_id = answer_data["questionId"]
        self.user_id = user_id
        self.question_type_id = answer_data.get("questionTypeId")
        self.user_answer = answer_data.get("userAnswer", "")
        self.correct_answer = answer_data.get("correctAnswer", "")
        self.constraints = answer_data.get("constraints", "")
        
        self.is_correct = False
        self.feedback = ""
        self.hint = ""
        self.points = 0
        
        self.started_at = answer_data.get("startTime", datetime.utcnow())
        if not isinstance(self.started_at, datetime):
            try:
                self.started_at = datetime.fromtimestamp(self.started_at)
            except (TypeError, ValueError):
                self.started_at = datetime.utcnow()
                
        self.completed_at = datetime.utcnow()
        

        self.retry = self.get_retry_count()
        self.skill_level = skill_level

    def get_retry_count(self):
        try:
            response = (
                supabase_client.table("Answer")
                .select("retry")
                .eq("userID", self.user_id)
                .eq("questionID", self.question_id)
                .maybe_single()
                .execute()
            )
            if response.data:
                return response.data.get("retry", 0) + 1
            return 1
        except Exception:
            return 1

    def calculate_time_taken(self):
        return int((self.completed_at - self.started_at).total_seconds())

    def validate(self):
        def parse_response(raw):
            if isinstance(raw, dict):
                if "error" in raw:
                    raise Exception(raw["error"])
                return raw
            try:
                return json.loads(raw)
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON from model: {str(e)}")

        #time taken
        time_taken = self.calculate_time_taken()

        # avg time from DB
        try:
            res = supabase_client.table("Question").select("avgTimeSeconds").eq("questionID", self.question_id).single().execute()
            avg_time = res.data.get("avgTimeSeconds", 90)
        except Exception:
            avg_time = 90

        # MCQ & Drag-Drop
        if self.question_type_id in (1, 4):
            self.is_correct = self.user_answer == self.correct_answer
            if not self.is_correct:
                self.feedback = "Not quite right"

        # Coding
        elif self.question_type_id == 2:
            req = {
                "questionid": self.question_id,
                "question": self.correct_answer,
                "user_answer": self.user_answer,
                "constraints": self.constraints,
                "avgTimeSeconds": avg_time,
                "timeTaken": time_taken
            }
            raw_response = Prompt.check_coding(json.dumps(req))
            response = parse_response(raw_response)

            self.is_correct = response.get("isCorrect", False)
            self.feedback = response.get("feedback", "")
            self.hint = response.get("hint", "")
            self.points = response.get("points") or ScoreCalculator.BASE_POINTS.get(self.question_type_id, 0)

        #fill-in-the-blank
        elif self.question_type_id == 3:
            req = {
                "questionid": self.question_id,
                "user_answer": self.user_answer,
                "correct_answer": self.correct_answer,
                "avgTimeSeconds": avg_time,
                "timeTaken": time_taken
            }
            raw_response = Prompt.check_fill_in(json.dumps(req))
            response = parse_response(raw_response)

            self.is_correct = response.get("isCorrect", False)
            self.feedback = response.get("feedback", "")
            self.hint = response.get("hint", "")
            self.points = response.get("points") or ScoreCalculator.BASE_POINTS.get(self.question_type_id, 0)

    def apply_scoring(self):
        try:
            res = supabase_client.table("Question").select("avgTimeSeconds").eq("questionID", self.question_id).single().execute()
            avg_time = res.data.get("avgTimeSeconds", 120)
        except Exception:
            avg_time = 120

        time_taken = self.calculate_time_taken()

        #bonus
        self.points = ScoreCalculator.calculate_points(
            question_type_id=self.question_type_id,
            is_correct=self.is_correct,
            retry=self.retry,
            time_taken=time_taken,
            skill_level=self.skill_level,
            avg_time=avg_time,
            base_score=self.points if self.points > 0 else None
        )

    def persist(ans):
        try:
            # Convert datetime objects to timestamps for storage
            started_timestamp = int(ans.started_at.timestamp()) if isinstance(ans.started_at, datetime) else ans.started_at
            completed_timestamp = int(ans.completed_at.timestamp()) if isinstance(ans.completed_at, datetime) else ans.completed_at
            
            # Check if answer already exists
            existing = (
                supabase_client.table("Answer")
                .select("answerID")
                .eq("userID", ans.user_id)
                .eq("questionID", ans.question_id)
                .single()
                .execute()
            )

            if existing.data:
                response = (
                    supabase_client.table("Answer")
                    .update({
                        "userAnswer": ans.user_answer,
                        "correctAnswer": ans.correct_answer,
                        "correct": ans.is_correct,
                        "feedback": ans.feedback,
                        "hint": ans.hint,
                        "points": ans.points,
                        "retry": ans.retry,
                        "startedAt": started_timestamp,
                        "completedAt": completed_timestamp
                    })
                    .eq("answerID", existing.data["answerID"])
                    .execute()
                )
            else:
                response = (
                    supabase_client.table("Answer")
                    .insert([{
                        "questionID": ans.question_id,
                        "userID": ans.user_id,
                        "userAnswer": ans.user_answer,
                        "correctAnswer": ans.correct_answer,
                        "correct": ans.is_correct,
                        "feedback": ans.feedback,
                        "hint": ans.hint,
                        "points": ans.points,
                        "retry": ans.retry,
                        "startedAt": started_timestamp,
                        "completedAt": completed_timestamp
                    }])
                    .execute()
                )

            return {"success": True, "data": response.data}
        except Exception as e:
            return {"success": False, "error": str(e), "status": 500}
        
    @staticmethod
    def submit_answers(user_id, answers_data, skill_level):
        results = []
        
        for answer_data in answers_data:
            try:
                answer = Answer(answer_data, user_id, skill_level)
                answer.validate()
                answer.apply_scoring()
                result = answer.persist()
                
                if result["success"]:
                    results.append({
                        "questionId": answer.question_id,
                        "success": True,
                        "isCorrect": answer.is_correct,
                        "points": answer.points,
                        "feedback": answer.feedback,
                        "hint": answer.hint
                    })
                else:
                    results.append({
                        "questionId": answer.question_id,
                        "success": False,
                        "error": result["error"]
                    })
            except Exception as e:
                results.append({
                    "questionId": answer_data.get("questionId", "unknown"),
                    "success": False,
                    "error": str(e)
                })
                
        return results