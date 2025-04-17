from config.settings import supabase_client
from datetime import datetime, timezone

class MissionService:
    @staticmethod
    def get_missions(user_id):
        try:
            # Get all missions
            missions_response = supabase_client.from_("Missions").select("*").execute()
            
            if not missions_response.data:
                return [], 200
                
            # Get user's completed missions
            user_missions_response = supabase_client.from_("UserMissions") \
                .select("*") \
                .eq("userID", user_id) \
                .execute()
                
            user_missions = {um["missionID"]: um for um in user_missions_response.data} if user_missions_response.data else {}
            
            # Format the response
            missions_data = []
            for mission in missions_response.data:
                mission_id = mission["missionID"]
                mission_status = {
                    "missionID": mission_id,
                    "question": mission["missionQuestion"],
                    "isCompleted": mission_id in user_missions,
                    "isCorrect": user_missions.get(mission_id, {}).get("isCorrect", None),
                    "points": mission["points"]
                }
                missions_data.append(mission_status)
                
            return missions_data, 200
        except Exception as e:
            print(f"Error fetching missions: {e}")
            return {"error": str(e)}, 500
    
    @staticmethod
    def get_mission_details(user_id, mission_id):
        try:
            # Get mission details
            mission_response = supabase_client.from_("Missions") \
                .select("*") \
                .eq("missionID", mission_id) \
                .execute()
                
            if not mission_response.data:
                return {"error": "Mission not found"}, 404
                
            mission = mission_response.data[0]
            
            # Check if user has already completed this mission
            user_mission_response = supabase_client.from_("UserMissions") \
                .select("*") \
                .eq("userID", user_id) \
                .eq("missionID", mission_id) \
                .execute()
                
            has_completed = bool(user_mission_response.data)
            
            # Format response
            mission_details = {
                "missionID": mission["missionID"],
                "question": mission["missionQuestion"],
                "options": {
                    "A": mission["optionA"],
                    "B": mission["optionB"],
                    "C": mission["optionC"],
                    "D": mission["optionD"]
                },
                "isCompleted": has_completed,
                "points": mission["points"]
            }
            
            # If mission is completed, include the results
            if has_completed:
                user_mission = user_mission_response.data[0]
                mission_details["userAnswer"] = user_mission["userAnswer"]
                mission_details["isCorrect"] = user_mission["isCorrect"]
                mission_details["correctAnswer"] = mission["correctAnswer"]
            
            return mission_details, 200
        except Exception as e:
            print(f"Error fetching mission details: {e}")
            return {"error": str(e)}, 500

    @staticmethod
    def answer_mission(user_id, mission_id, answer):
        try:
            # Check if mission exists
            mission_response = supabase_client.from_("Missions") \
                .select("*") \
                .eq("missionID", mission_id) \
                .execute()
                    
            if not mission_response.data:
                return {"error": "Mission not found"}, 404
                    
            mission = mission_response.data[0]
            
            # Check if user has already completed this mission
            user_mission_response = supabase_client.from_("UserMissions") \
                .select("*") \
                .eq("userID", user_id) \
                .eq("missionID", mission_id) \
                .execute()
                    
            if user_mission_response.data:
                return {"error": "Mission already completed"}, 400
            
            # Check if answer is correct
            is_correct = answer == mission["correctAnswer"]
            points_earned = mission["points"] if is_correct else 0
            
            # Record user's answer
            now = datetime.now(timezone.utc)
            supabase_client.from_("UserMissions").insert({
                "userID": user_id,
                "missionID": mission_id,
                "userAnswer": answer,
                "isCorrect": is_correct,
            }).execute()
            
            # If correct, update user's points
            if is_correct:
                user_response = supabase_client.from_("User") \
                    .select("points") \
                    .eq("userID", user_id) \
                    .execute()
                
                if user_response.data:
                    current_points = user_response.data[0]["points"]
                    new_points = current_points + points_earned
                    
                    supabase_client.from_("User") \
                        .update({"points": new_points}) \
                        .eq("userID", user_id) \
                        .execute()
            
            return {
                "isCorrect": is_correct,
                "correctAnswer": mission["correctAnswer"],
                "pointsEarned": points_earned
            }, 200
        except Exception as e:
            print(f"Error answering mission: {e}")
            return {"error": str(e)}, 500