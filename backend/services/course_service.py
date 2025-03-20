from config.settings import supabase_client

class CourseService:
    @staticmethod
    def get_courses():
        try:
            response = supabase_client.table("RefUnit").select("unitID, unitName,unitDescription, RefSubUnit(subUnitID, subUnitName)").execute()
            if response.data:
                return response.data, 200
            else:
                return {"error": "No courses found"}, 404
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
            if response.data:
                return response.data, 201
            else:
                return {"error": "Failed to add course"}, 500
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_questions():
        try:
            response = (
                supabase_client.table("Question")
                .select("*")
                .eq("lessonID", 1)
                .limit(5)
                .execute()
            )
            print(response.data)
            if response.data:
                return response.data, 200
            else:
                return {"error": "No questions found"}, 404
        except Exception as e:
            return {"error": str(e)}, 500
        