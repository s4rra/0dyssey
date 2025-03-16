from config.settings import supabase_client

class CourseService:
    @staticmethod
    def get_courses():
        try:
            response = supabase_client.table("RefUnit").select("unitID, unitName, RefSubUnit(subUnitID, subUnitName)").execute()
            return response.data if response.data else {"error": "No courses found"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def add_course(data):
        try:
            new_course = {
                "unitID": data.get("unitID"),
                "unitName": data.get("unitName"),
            }
            response = supabase_client.table("RefUnit").insert(new_course).execute()
            return response.data if response.data else {"error": "Failed to add course"}, 201
        except Exception as e:
            return {"error": str(e)}, 500
