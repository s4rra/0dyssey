import json
from prompt import *
from config.settings import supabase_client
from services.user_service import *
#service class
class Questions:
    @staticmethod
    def fetch_questions_by_type(subunit_id, question_type_id, limit):
        try:
            fields = "questionID, questionText, correctAnswer, options, questionTypeID, constraints, skilllevel, avgTimeSeconds"
            response = (
                supabase_client.table("Question")
                .select(fields)
                .eq("lessonID", subunit_id)
                .eq("questionTypeID", question_type_id)
                .eq("generated", True)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching questions type {question_type_id}:", e)
            return []
    
    @staticmethod
    def persist(question_data): 
        try:
            response = (
                supabase_client.table("Question")
                .insert([question_data])
                .execute()
            )
            print(response.data)
            return {"success": True, "data": response.data, "status": 201}
        except Exception as exception:
            return {"success": False, "error": str(exception), "status": 500}

    @staticmethod
    def get_questions(subunit_id, user):
        try:
            skill_level_id = user["chosenSkillLevel"]
            if skill_level_id not in [1, 2, 3]:
                return {"error": "Invalid skill level provided"}, 400

            if skill_level_id == 1:
                type_limits = {
                    1: 3,
                    3: 1,
                    4: 1
                }
            elif skill_level_id == 2:
                type_limits = {
                    1: 2,
                    3: 1,
                    4: 1,
                    2: 1
                }
            elif skill_level_id == 3:
                type_limits = {
                    3: 1,
                    2: 4
                }
            questions = []
            for q_type, limit in type_limits.items():
                questions.extend(Questions.fetch_questions_by_type(subunit_id, q_type, limit))

            if not questions:
                return {"error": "No questions found"}, 404

            return questions, 200

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def generate_questions(subunit_id, user):
        try:
            skill_level = user["chosenSkillLevel"]
            subunit_info = (
                supabase_client.table("RefSubUnit")
                .select("subUnitDescription, RefUnit(unitDescription)")
                .eq("subUnitID", subunit_id)
                .single()
                .execute()
            )

            if not subunit_info.data:
                return {"error": "Subunit not found"}, 404

            unitDescription = subunit_info.data["RefUnit"]["unitDescription"]
            subUnitDescription = subunit_info.data["subUnitDescription"]
            prompt = f"generate new questions for: unitDescription:({unitDescription}), subUnitDescription: ({subUnitDescription}), Skill Level is {skill_level} (Beginner=1, Intermediate=2, Advanced=3)"
            print(prompt)

            question_ids = []

            def process_questions(data, question_type_id):
                for q in data:
                    question_data = {
                        "questionTypeID": question_type_id,
                        "lessonID": subunit_id,
                        "questionText": q["question"],
                        "correctAnswer": q["correct_answer"],
                        "options": q.get("options", {}),
                        "constraints": q.get("constraints", ""),
                        "tags": q.get("tags", []),
                        "generated": True,
                        "skilllevel": skill_level,
                        "avgTimeSeconds": q.get("avgTimeSeconds", 120)
                    }
                    res = Questions.persist(question_data)
                    if not res["success"]:
                        raise Exception(res.get("error", "tests error"))
                    question_ids.append(res["data"][0]["questionID"])

            process_questions(json.loads(Prompt.generate_MCQ(prompt)), 1)
            process_questions(json.loads(Prompt.generate_coding(prompt)), 2)
            process_questions(json.loads(Prompt.generate_fill_in(prompt)), 3)
            process_questions(json.loads(Prompt.generate_drag_and_drop(prompt)), 4)

            return {"message": "Questions generated and stored", "question_ids": question_ids}, 200

        except Exception as e:
            return {"error": str(e)}, 500
        