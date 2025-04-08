from datetime import datetime #for calculating when the question started and ended
import json #parse and serialize data to/from the Prompt class
from prompt import Prompt # for validating coding/fill-in answers
from config.settings import supabase_client #database client connected

class ScoreCalculator:
    #only for MCQ and DragDrop (prompt types return points directly)
    BASE_POINTS = {
        1: 5,  # MCQ
        4: 8   # Drag-drop
    }
    
    #bonus based on skill level
    SKILL_BONUS = {
        1: 1,
        2: 2,
        3: 3
    }

    #base_score.... either fixed for MCQ/drag or returned from the prompt coding/fill
    @staticmethod
    def apply_bonuses(base_score, is_correct, retry, time_taken, avg_time, skill_level):
        if not is_correct:
            return 0

        skill_bonus = ScoreCalculator.SKILL_BONUS.get(skill_level, 0)
        retry_penalty = retry
        time_bonus = 4 if time_taken < avg_time else 0

        total = base_score + skill_bonus + time_bonus - retry_penalty
        return max(total, 1)

class Answer:
    def __init__(self, answer_data, user_id, skill_level=None):
        if isinstance(answer_data, str):
            answer_data = json.loads(answer_data)
        
        self.user_id = user_id
        self.question_id = answer_data["questionId"]
        self.question_type_id = answer_data.get("questionTypeId")
        self.user_answer = answer_data.get("userAnswer", "")
        self.start_time = answer_data.get("startTime")
        self.end_time = answer_data.get("endTime")
        self.skill_level = skill_level
        self.time_taken = max(1, int(self.end_time - self.start_time))

        self.question_text = ""
        self.correct_answer = ""
        self.constraints = ""
        self.avg_time = 90

        self.is_correct = False
        self.points = 0
        self.feedback = ""
        self.hint = ""
        self.retry = self.get_retry_count()

        self.load_question_metadata()

    def get_retry_count(self):
        try:
            res = supabase_client.table("Answer") \
                .select("retry") \
                .eq("userID", self.user_id) \
                .eq("questionID", self.question_id) \
                .maybe_single() \
                .execute()
            data = res.data
            if isinstance(data, str):
                data = json.loads(data)
            return data.get("retry", 0) + 1 if data else 0
        except Exception:
            return 0

    def load_question_metadata(self):
        try:
            res = supabase_client.table("Question") \
                .select("questionText", "correctAnswer", "constraints", "avgTimeSeconds") \
                .eq("questionID", self.question_id) \
                .single() \
                .execute()
            q = res.data
            if isinstance(q, str):
                q = json.loads(q)
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
            self.feedback = "Correct!" if self.is_correct else "Incorrect"
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
                
            existing = res.data
            if isinstance(existing, str):
                existing = json.loads(existing)

            payload = {
                "questionID": self.question_id,
                "userID": self.user_id,
                "userAnswer": self.user_answer,
                "correctAnswer": self.correct_answer,
                "correct": self.is_correct,
                "feedback": self.feedback if self.question_type_id in (2, 3) else "",
                "hint": self.hint if self.question_type_id in (2, 3) else "",
                "points": self.points,
                "retry": self.retry,
                "startedAt": self.start_time,
                "completedAt": self.end_time
            }
            
            if existing:
                supabase_client.table("Answer") \
                    .update(payload) \
                    .eq("answerID", existing["answerID"]) \
                    .execute()
            else:
                payload["retry"] = 0  # Ensure retry starts at 0
                supabase_client.table("Answer") \
                    .insert([payload]) \
                    .execute()

        except Exception as e:
            raise Exception("db save failed: " + str(e))


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
            # 🔍 SAFELY LOG EACH ENTRY
            print("🟡 ENTRY TYPE:", type(a))
            print("🟡 ENTRY VALUE:", a)

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
                    "hint": ans.hint
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
            if isinstance(user_data, str):
                user_data = json.loads(user_data)

            old_points = user_data.get("points", 0)
            new_total = old_points + total_points
            supabase_client.table("User") \
                .update({"points": new_total}) \
                .eq("userID", user_id) \
                .execute()
        except Exception as e:
            results.append({"error": "Failed to update user points: " + str(e)})

        return {"results": results}
