import json
from config.settings import supabase_client

class SubunitService:
    @staticmethod
    def get_subunit_content(subunit_id):
        try:
            response = (
                supabase_client.from_("RefSubUnit")
                .select("subUnitID, subUnitName, subUnitDescription, subUnitContent")
                .eq("subUnitID", subunit_id)
                .execute()
            )
            
            if not response.data:
                return {"error": "Subunit not found"}, 404
            
            subunit = response.data[0]
            
            # If content is a JSON string, try parsing it
            if isinstance(subunit.get('subUnitContent'), str):
                try:
                    subunit['subUnitContent'] = json.loads(subunit['subUnitContent'])
                except json.JSONDecodeError:
                    pass

            return subunit, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def add_subunit(data): 
        try:
            new_subunit = {
                "subUnitName": data.get("subUnitName"),
                "subUnitDescription": data.get("subUnitDescription", ""),
                "subUnitContent": json.dumps(data.get("subUnitContent", "")),
            }
            response = supabase_client.from_("RefSubUnit").insert(new_subunit).execute()
            
            if response.data:
                return response.data, 201
            else:
                return {"error": "Failed to add subunit"}, 500
        
        except Exception as e:
            return {"error": str(e)}, 500
    
    @staticmethod
    def mark_subunit_completed(user_id, subunit_id):
        try:
            # Check if record already exists
            existing = supabase_client.from_("UserProgress").select("*").eq("userID", user_id).eq("subUnitID", subunit_id).execute()
            
            progress_data = {
                "userID": user_id,
                "subUnitID": subunit_id,
                "isCompleted": True
                # completionDate will use database default now()
            }
            
            if existing.data:
                # Update existing record
                response = supabase_client.from_("UserProgress").update(progress_data).eq("userID", user_id).eq("subUnitID", subunit_id).execute()
            else:
                # Insert new record
                response = supabase_client.from_("UserProgress").insert(progress_data).execute()
            
            if response.data:
                return {"message": "Subunit marked as completed"}, 200
            else:
                return {"error": "Failed to mark completion"}, 500
        
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def can_access_subunit(user_id, subunit_id):
        try:
            # Get the requested subunit info
            subunit_response = supabase_client.from_("RefSubUnit").select("unitID, subUnitID").eq("subUnitID", subunit_id).execute()
            
            if not subunit_response.data:
                return {"accessible": False, "reason": "Subunit not found"}, 404
                
            unit_id = subunit_response.data[0]["unitID"]
            
            # First check if this is the very first subunit of the very first unit
            # Get all units ordered by ID
            all_units = supabase_client.from_("RefUnit").select("unitID").order("unitID").execute()
            unit_ids = [u["unitID"] for u in all_units.data]
            
            # Get all subunits in the requested unit, ordered by ID
            unit_subunits = supabase_client.from_("RefSubUnit").select("subUnitID").eq("unitID", unit_id).order("subUnitID").execute()
            subunit_ids = [s["subUnitID"] for s in unit_subunits.data]
            
            # Find current subunit position
            current_index = subunit_ids.index(subunit_id) if subunit_id in subunit_ids else -1
            if current_index == -1:
                return {"accessible": False, "reason": "Invalid subunit ID"}, 404
            
            # Special case for the very first subunit of the very first unit
            if unit_ids and unit_id == unit_ids[0] and current_index == 0:
                return {"accessible": True}, 200
            
            # For all other subunits, check if the previous one is completed
            if current_index > 0:
                # Check previous subunit in same unit
                previous_subunit_id = subunit_ids[current_index - 1]
                completion_check = supabase_client.from_("UserProgress").select("isCompleted").eq("userID", user_id).eq("subUnitID", previous_subunit_id).eq("isCompleted", True).execute()
                
                if completion_check.data:
                    return {"accessible": True}, 200
                else:
                    return {"accessible": False, "reason": "You must complete the previous lesson first"}, 403
            else:
                # This is the first subunit in a unit (but not the first unit)
                # Find previous unit
                unit_index = unit_ids.index(unit_id) if unit_id in unit_ids else -1
                if unit_index <= 0:
                    # Safety check - this shouldn't happen based on our earlier check
                    return {"accessible": False, "reason": "Invalid unit sequence"}, 403
                
                previous_unit_id = unit_ids[unit_index - 1]
                
                # Get the last subunit of the previous unit
                prev_unit_subunits = supabase_client.from_("RefSubUnit").select("subUnitID").eq("unitID", previous_unit_id).order("subUnitID").execute()
                if not prev_unit_subunits.data:
                    # No subunits in previous unit, so allow access
                    return {"accessible": True}, 200
                    
                last_subunit_id = prev_unit_subunits.data[-1]["subUnitID"]
                
                # Check if last subunit of previous unit is completed
                completion_check = supabase_client.from_("UserProgress").select("isCompleted").eq("userID", user_id).eq("subUnitID", last_subunit_id).eq("isCompleted", True).execute()
                
                if completion_check.data:
                    return {"accessible": True}, 200
                else:
                    return {"accessible": False, "reason": "You must complete all lessons in the previous unit first"}, 403
        
        except Exception as e:
            return {"accessible": False, "error": str(e)}, 500

    @staticmethod
    def get_user_progress(user_id):
        try:
            # Get all completed subunits for this user
            response = supabase_client.from_("UserProgress").select("subUnitID, completionDate, isCompleted").eq("userID", user_id).eq("isCompleted", True).execute()
            
            if response.data:
                return {"completed_subunits": response.data}, 200
            else:
                return {"completed_subunits": []}, 200
        
        except Exception as e:
            return {"error": str(e)}, 500