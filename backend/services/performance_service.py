import json
from datetime import datetime
from prompt import Prompt
from config.settings import supabase_client

class PerformanceService:
    def __init__(self, user_id):
        self.user_id = user_id

    def update_performance(self, unit_id, subunit_id, answers):
        try:
            total_questions = len(answers)
            correct_answers = 0
            total_time_taken = 0
            tag_performance = {}

            for answer in answers:
                if answer.get("isCorrect", False):
                    correct_answers += 1
                total_time_taken += answer.get("timeTaken", 0)

                question_id = answer.get("questionId")
                if question_id:
                    question = supabase_client.table("Question") \
                        .select("tags") \
                        .eq("questionID", question_id) \
                        .maybe_single() \
                        .execute()
                    tags = question.data.get("tags", []) if question.data else []
                    for tag in tags:
                        if tag not in tag_performance:
                            tag_performance[tag] = {"correct": 0, "total": 0}
                        tag_performance[tag]["total"] += 1
                        if answer.get("isCorrect", False):
                            tag_performance[tag]["correct"] += 1

            avg_time = total_time_taken // total_questions if total_questions else 0

            performance_data = {
                "points": sum(answer.get("points", 0) for answer in answers),
                "unitID": unit_id,
                "subUnitID": subunit_id,
                "userID": self.user_id,
                "totalQuestions": total_questions,
                "correctAnswers": correct_answers,
                "totalTimeTaken": total_time_taken,
                "avgTime": avg_time,
                "tags": tag_performance,
                "updatedAt": datetime.now().isoformat()
            }

            result = supabase_client.table("Performance") \
                .insert(performance_data) \
                .execute()

            return {
                "success": True,
                "performanceID": result.data[0].get("performanceID") if result.data else None
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_skill_level(self, new_level):
            try:
                result = supabase_client.table("User") \
                    .update({"chosenSkillLevel": new_level}) \
                    .eq("userID", self.user_id) \
                    .execute()
                if not result.data:
                    return {"success": False, "error": "Skill level update failed"}
                    
                return {"success": True, "newLevel": new_level}
                
            except Exception as e:
                print(f"Error updating skill level: {str(e)}")
                return {"success": False, "error": str(e)}
        
    def get_performance_history(self, subunit_id, limit=5):
        try:
            result = supabase_client.table("Performance") \
                .select("*") \
                .eq("userID", self.user_id) \
                .eq("subUnitID", subunit_id) \
                .order("updatedAt", desc=True) \
                .limit(limit) \
                .execute()
            return result.data or []
        except Exception as e:
            return []

    def get_performance_for_unit(self, unit_id):
        try:
            subunits = supabase_client.table("RefSubUnit") \
                .select("subUnitID") \
                .eq("unitID", unit_id) \
                .execute()

            if not subunits.data:
                return []

            performance_data = []
            for subunit in subunits.data:
                subunit_id = subunit["subUnitID"]
                history = self.get_performance_history(subunit_id)
                performance_data.extend(history)

            return performance_data

        except Exception as e:
            return []

    def get_tag_performance(self):
        try:
            result = supabase_client.table("Performance") \
                .select("tags") \
                .eq("userID", self.user_id) \
                .execute()

            all_tags = {}
            for entry in result.data or []:
                for tag, value in entry.get("tags", {}).items():
                    if tag not in all_tags:
                        all_tags[tag] = {"correct": 0, "total": 0}
                    all_tags[tag]["correct"] += value.get("correct", 0)
                    all_tags[tag]["total"] += value.get("total", 0)

            tag_performance = {}
            for tag, stats in all_tags.items():
                if stats["total"] > 0:
                    tag_performance[tag] = {
                        **stats,
                        "percentage": round((stats["correct"] / stats["total"]) * 100, 2)
                    }

            return tag_performance
        except Exception as e:
            return {}

    def get_summary(self, skill_level=None, performance_data=None):
        try:
            if skill_level is None:
                skill_level = supabase_client.table("User") \
                    .select("chosenSkillLevel") \
                    .eq("userID", self.user_id) \
                    .single() \
                    .execute().data.get("chosenSkillLevel", "beginner")

            if not performance_data:
                performance_data = supabase_client.table("Performance") \
                    .select("*") \
                    .eq("userID", self.user_id) \
                    .order("updatedAt", desc=True) \
                    .limit(5) \
                    .execute().data or []

            subunit_map = {}
            for perf in performance_data:
                subunit_id = perf["subUnitID"]
                if subunit_id not in subunit_map:
                    subunit_map[subunit_id] = []
                subunit_map[subunit_id].append(perf)

            feedback_items = []

            for subunit_id, history in subunit_map.items():
                prompt_input = {
                    "currentSkillLevel": skill_level,
                    "performanceHistory": history
                }

                feedback = Prompt.check_performance(json.dumps(prompt_input))
                feedback = json.loads(feedback)

                if not feedback or "error" in feedback:
                    continue

                latest_id = history[0].get("performanceID")
                if latest_id:
                    supabase_client.table("Performance") \
                        .update({"aiSummary": feedback.get("aiSummary", "")}) \
                        .eq("performanceID", latest_id) \
                        .execute()

                feedback_items.append({
                    "subUnitID": subunit_id,
                    "aiSummary": feedback.get("aiSummary", "")
                })

            return feedback_items

        except Exception as e:
            return []

    def model_feedback(self, unit_id, skill_level):
        try:
            unit_info = supabase_client.table("RefUnit") \
                .select("unitDescription") \
                .eq("unitID", unit_id) \
                .single() \
                .execute()

            unit_description = unit_info.data.get("unitDescription", "")

            # 🧠 Get all user performance for the unit
            performance_data = self.get_performance_for_unit(unit_id)
            if not performance_data:
                return {"success": False, "error": "No performance data found"}

            # ✅ Smart Check: has the user completed every subunit in this unit?
            subunits_resp = supabase_client.table("RefSubUnit") \
                .select("subUnitID") \
                .eq("unitID", unit_id) \
                .execute()

            expected_subunit_ids = {s["subUnitID"] for s in subunits_resp.data}
            completed_subunit_ids = {p["subUnitID"] for p in performance_data}

            if not expected_subunit_ids.issubset(completed_subunit_ids):
                return {
                    "success": False,
                    "error": "User must complete all subunits before unit analysis.",
                    "missingSubunits": list(expected_subunit_ids - completed_subunit_ids)
                }

            # 🧠 Continue with tag + AI feedback
            tag_data = self.get_tag_performance()

            prompt_input = {
                "unitDescription": unit_description,
                "currentSkillLevel": skill_level,
                "subunitPerformance": performance_data,
                "tagPerformance": tag_data
            }

            ai_feedback = Prompt.check_performance(json.dumps(prompt_input))
            ai_feedback = json.loads(ai_feedback)

            if "error" in ai_feedback:
                return {"success": False, "error": "AI feedback failed"}

            # ✅ Insert unitPerformance only when complete
            supabase_client.table("unitPerformance") \
                .insert({
                    "userID": self.user_id,
                    "unitID": unit_id,
                    "aiSummary": ai_feedback.get("aiSummary", ""),
                    "feedbackPrompt": ai_feedback.get("feedbackPrompt", ""),
                    "levelSuggestion": ai_feedback.get("levelSuggestion"),
                    "tagPerformance": tag_data,
                    "created_at": datetime.now().isoformat()
                }).execute()

            subunit_feedback = self.get_summary(skill_level, performance_data)

            return {
                "success": True,
                "feedback": ai_feedback,
                "subunitFeedback": subunit_feedback
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
    