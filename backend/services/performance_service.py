import json
from datetime import datetime, timezone
from prompt import Prompt
from config.settings import supabase_client

class PerformanceService:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def update_subunit_performance(self, unit_id, subunit_id, answers):
        try:
            # Initialize counters
            total_questions = len(answers)
            correct_answers = 0
            total_time_taken = 0
            tag_performance = {}
            
            # Process each answer to gather metrics
            for answer in answers:
                # Add to correct count if answer was correct
                if answer.get("isCorrect", False):
                    correct_answers += 1
                # Add time taken
                total_time_taken += answer.get("timeTaken", 0)
                
                # Process tags - fetch question tags from database
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
                            # Initialize tag if not exists
                            if tag not in tag_performance:
                                tag_performance[tag] = {"correct": 0, "total": 0}
                            
                            # Increment tag counters
                            tag_performance[tag]["total"] += 1
                            if answer.get("isCorrect", False):
                                tag_performance[tag]["correct"] += 1
            
            # Calculate average time
            avg_time = total_time_taken // total_questions if total_questions > 0 else 0
            
            # Create new performance record
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
            
            # Insert into Performance table
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
    
    def get_latest_performance_by_subunit(self, subunit_id):
        try:
            result = supabase_client.table("Performance") \
                .select("*") \
                .eq("userID", self.user_id) \
                .eq("subUnitID", subunit_id) \
                .order("updatedAt", desc=True) \
                .limit(1) \
                .maybe_single() \
                .execute()
                
            return result.data if result.data else None
            
        except Exception as e:
            print(f"Error getting latest performance: {str(e)}")
            return None
    
    def get_latest_performance_for_unit(self, unit_id):
        try:
            # First get all subunits for this unit
            subunits = supabase_client.table("RefSubUnit") \
                .select("subUnitID, subUnitDescription") \
                .eq("unitID", unit_id) \
                .execute()
                
            if not subunits.data:
                return []
                
            # For each subunit, get the latest performance data
            latest_performances = []
            for subunit in subunits.data:
                subunit_id = subunit.get("subUnitID")
                performance = self.get_latest_performance_by_subunit(subunit_id)
                
                if performance:
                    # Add subunit description to performance data
                    performance["subUnitDescription"] = subunit.get("subUnitDescription", "")
                    latest_performances.append(performance)
            
            return latest_performances
            
        except Exception as e:
            print(f"Error getting unit performance: {str(e)}")
            return []
    
    def generate_ai_feedback(self, unit_id):
        try:
            # Get unit information
            unit_info = supabase_client.table("RefUnit") \
                .select("unitDescription, skillLevelID") \
                .eq("unitID", unit_id) \
                .single() \
                .execute()
                
            if not unit_info.data:
                return {"success": False, "error": "Unit not found"}
                
            unit_description = unit_info.data.get("unitDescription", "")
            current_skill_level = unit_info.data.get("skillLevelID", 1)
            
            # Get latest performance for all subunits in this unit
            performance_data = self.get_latest_performance_for_unit(unit_id)
            
            if not performance_data:
                return {"success": False, "error": "No performance data found"}
                
            # Prepare data for AI prompt
            prompt_data = {
                "unitDescription": unit_description,
                "currentSkillLevel": current_skill_level,
                "subunitPerformance": performance_data,
                "userId": self.user_id
            }
            
            # Call Gemini AI via Prompt
            ai_feedback = Prompt.check_performance(json.dumps(prompt_data)) 
            
            if not ai_feedback or "error" in ai_feedback:
                return {"success": False, "error": "Failed to generate AI feedback"}
                
            # Update each subunit's latest performance with AI feedback
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
    
    def get_dashboard_summary(self):
        try:
            # Get list of all subunits the user has attempted
            distinct_subunits_query = """
                SELECT DISTINCT "subUnitID" 
                FROM "Performance" 
                WHERE "userID" = '{}'
            """.format(self.user_id)
            
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
                    performance = self.get_latest_performance_by_subunit(subunit_id)
                    if performance:
                        # Get subunit info
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