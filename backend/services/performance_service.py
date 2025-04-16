import json
from datetime import datetime, timezone
from prompt import Prompt
from config.settings import supabase_client

class PerformanceService:
    def __init__(self, user_id):
        self.user_id = user_id
        
    def update_performance(self, unit_id, subunit_id, answers):
        try:
            # Process metrics from answers
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
                    
                    if question.data and question.data.get("tags"):
                        tags = question.data.get("tags", [])
                        for tag in tags:
                            if tag not in tag_performance:
                                tag_performance[tag] = {"correct": 0, "total": 0}
                            
                            tag_performance[tag]["total"] += 1
                            if answer.get("isCorrect", False):
                                tag_performance[tag]["correct"] += 1
            
            avg_time = total_time_taken // total_questions if total_questions > 0 else 0
            
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
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }
            
            result = supabase_client.table("Performance") \
                .insert(performance_data) \
                .execute()
                
            return {
                "success": True, 
                "performanceID": result.data[0].get("performanceID") if result.data else None
            }
            
        except Exception as e:
            print(f"Error updating performance: {str(e)}")
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
                
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting performance history: {str(e)}")
            return []
    
    def get_performance_for_unit(self, unit_id):
        try:
            subunits = supabase_client.table("RefSubUnit") \
                .select("subUnitID, subUnitDescription") \
                .eq("unitID", unit_id) \
                .execute()
                
            if not subunits.data:
                return []
                
            latest_performances = []
            for subunit in subunits.data:
                subunit_id = subunit.get("subUnitID")
                performance_list = self.get_performance_history(subunit_id)
                if performance_list:
                    latest = performance_list[0] 
                    latest["subUnitDescription"] = subunit.get("subUnitDescription", "")
                    latest_performances.append(latest)
                        
            return latest_performances
            
        except Exception as e:
            print(f"Error getting unit performance: {str(e)}")
            return []

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
    ####
    def model_feedback(self, unit_id, skill_level):
        try:
            unit_info = supabase_client.table("RefUnit") \
                .select("unitDescription") \
                .eq("unitID", unit_id) \
                .single() \
                .execute()
                
            if not unit_info.data:
                return {"success": False, "error": "Unit not found"}
                
            unit_description = unit_info.data.get("unitDescription", "")
            performance_data = self.get_performance_for_unit(unit_id)
            if not performance_data:
                return {"success": False, "error": "No performance data found"}
            
            #tag_performance = self.get_tag_performance()
              
            prompt_data = {
                "unitDescription": unit_description,
                "currentSkillLevel": skill_level,
                "subunitPerformance": performance_data,
                #"tagPerformance": tag_performance
            }
            ai_feedback = Prompt.check_performance(json.dumps(prompt_data))
            ai_feedback = json.loads(ai_feedback) 
            if not ai_feedback or "error" in ai_feedback:
                return {"success": False, "error": "Failed to generate AI feedback"}

            for performance in performance_data:
                performance_id = performance.get("performanceID")
                if performance_id:
                    supabase_client.table("Performance") \
                        .update({
                            "aiSummary": ai_feedback.get("aiSummary", ""),
                            "levelSuggestion": ai_feedback.get("levelSuggestion"),
                            "feedbackPrompt": ai_feedback.get("feedbackPrompt", "")
                        }) \
                        .eq("performanceID", performance_id) \
                        .execute()
            return {
                "success": True,
                "feedback": ai_feedback
            }
        except Exception as e:
            print(f"Error generating AI feedback: {str(e)}")
            return {"success": False, "error": str(e)}
    
    ########
    def get_tag_performance(self):
            try:
                performances = supabase_client.table("Performance") \
                    .select("tags") \
                    .eq("userID", self.user_id) \
                    .order("updatedAt", desc=True) \
                    .execute()
                
                if not performances.data:
                    return {}
                
                all_tags = {}
                for performance in performances.data:
                    tags = performance.get("tags", {})
                    for tag, metrics in tags.items():
                        if tag not in all_tags:
                            all_tags[tag] = {"correct": 0, "total": 0}
                        
                        all_tags[tag]["correct"] += metrics.get("correct", 0)
                        all_tags[tag]["total"] += metrics.get("total", 0)
                
                tag_performance = {}
                for tag, metrics in all_tags.items():
                    if metrics["total"] > 0:
                        percentage = (metrics["correct"] / metrics["total"]) * 100
                        tag_performance[tag] = {
                            "correct": metrics["correct"],
                            "total": metrics["total"],
                            "percentage": round(percentage, 2)
                        }
                
                return tag_performance
                
            except Exception as e:
                print(f"Error analyzing tag performance: {str(e)}")
                return {}
    
    def get_summary(self):
        try:
            # Get list of all subunits the user has attempted
            distinct_subunits = supabase_client.rpc('get_distinct_subunits', {
                'user_id': self.user_id
            }).execute()

            if not distinct_subunits.data:
                return []
                
            # For each subunit, get the latest performance
            dashboard_items = []
            for subunit_record in distinct_subunits.data:
                subunit_id = subunit_record.get("subUnitID")
                if subunit_id:
                    performance = self.get_performance_history(subunit_id)
                    if performance:
                        # Get subunit and unit info
                        subunit_info = supabase_client.table("RefSubUnit") \
                            .select("subUnitDescription, RefUnit(unitDescription, unitID)") \
                            .eq("subUnitID", subunit_id) \
                            .single() \
                            .execute()
                            
                        if subunit_info.data:
                            # Add unit and subunit info to performance data
                            performance["subUnitDescription"] = subunit_info.data.get("subUnitDescription", "")
                            performance["unitDescription"] = subunit_info.data.get("RefUnit", {}).get("unitDescription", "")
                            performance["unitID"] = subunit_info.data.get("RefUnit", {}).get("unitID")
                            
                            dashboard_items.append(performance)

            return dashboard_items

        except Exception as e:
            print(f"Error getting dashboard summary: {str(e)}")
            return []
