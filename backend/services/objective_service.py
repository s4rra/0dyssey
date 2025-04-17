from config.settings import supabase_client

class ObjectiveService:
    @staticmethod
    def get_user_objectives(user_id):
        """Fetch objectives (subunits) and their completion status for a user."""
        try:
            # Get all subunits as potential objectives
            all_subunits = supabase_client.from_("RefSubUnit") \
                .select("subUnitID, subUnitName, unitID") \
                .execute()
            
            # Get completed subunits for this user
            completed_subunits = supabase_client.from_("UserProgress") \
                .select("subUnitID, pointsAwarded") \
                .eq("userID", user_id) \
                .execute()
            
            # Create a set of completed subunit IDs for easier lookup
            completed_ids = {item["subUnitID"]: item["pointsAwarded"] 
                            for item in completed_subunits.data}
            
            # Format the objectives data
            objectives = []
            for subunit in all_subunits.data:
                completed = subunit["subUnitID"] in completed_ids
                objectives.append({
                    "subUnitID": subunit["subUnitID"],
                    "subUnitName": subunit["subUnitName"],
                    "unitID": subunit["unitID"],
                    "completed": completed,
                    "pointsAwarded": completed_ids.get(subunit["subUnitID"], False) if completed else False
                })
            
            return {"objectives": objectives}, 200
            
        except Exception as e:
            print(f"Error fetching objectives: {e}")
            return {"error": str(e)}, 500
    
    @staticmethod
    def complete_objective(user_id, subunit_id):
        """Mark a subunit as completed and award points to the user."""
        try:
            # Check if already completed to prevent duplicate points
            existing = supabase_client.from_("UserProgress") \
                .select("progressID") \
                .eq("userID", user_id) \
                .eq("subUnitID", subunit_id) \
                .execute()
            
            if existing.data:
                return {"message": "Subunit already completed", "pointsAwarded": 0}, 200
            
            # Add progress record
            progress_data = {
                "userID": user_id,
                "subUnitID": subunit_id,
                "completed": True,
                "completedDate": "now()",
                "pointsAwarded": True
            }
            
            supabase_client.from_("UserProgress").insert(progress_data).execute()
            
            # Add points to user
            POINTS_PER_OBJECTIVE = 10
            user_response = supabase_client.from_("User") \
                .select("points") \
                .eq("userID", user_id) \
                .execute()
            
            if user_response.data:
                current_points = user_response.data[0]["points"]
                supabase_client.from_("User") \
                    .update({"points": current_points + POINTS_PER_OBJECTIVE}) \
                    .eq("userID", user_id) \
                    .execute()
            
            return {
                "message": "Objective completed successfully", 
                "pointsAwarded": POINTS_PER_OBJECTIVE
            }, 200
            
        except Exception as e:
            print(f"Error completing objective: {e}")
            return {"error": str(e)}, 500