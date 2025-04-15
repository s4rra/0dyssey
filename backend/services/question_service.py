import json
from prompt import *
from config.settings import supabase_client
from services.user_service import *

class Questions:
    def __init__(self,
                    question_type_id: int,
                    lesson_id: int,
                    correct_answer: str,
                    question_text: str,
                    options: dict,
                    tags: list,
                    constraints: str,
                    generated: bool,
                    skilllevel: int,
                    avgTimeSeconds: int):
            
            self.question_type_id = question_type_id
            self.lesson_id = lesson_id
            self.correct_answer = correct_answer
            self.question_text = question_text
            self.options = options
            self.tags = tags
            self.constraints = constraints
            self.generated = generated
            self.skilllevel = skilllevel
            self.avgTimeSeconds = avgTimeSeconds

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

    def persist(question): 
        try:
            response = (
                supabase_client.table("Question")
                .insert([
                    {   
                        "questionTypeID": question.question_type_id,
                        "lessonID": question.lesson_id,
                        "correctAnswer": question.correct_answer,
                        "questionText": question.question_text,
                        "options": question.options,
                        "tags": question.tags,
                        "constraints": question.constraints,
                        "generated": True,
                        "skilllevel": question.skilllevel,
                        "avgTimeSeconds": question.avgTimeSeconds
                    }
                ])
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
                    1: 3,  # MCQ
                    3: 1,  # Fill-in
                    4: 1   # Drag-Drop
                    # No coding
                }
            elif skill_level_id == 2:
                type_limits = {
                    1: 2,
                    3: 1,
                    4: 1,
                    2: 1  # 1 Coding
                }
            elif skill_level_id == 3:
                type_limits = {
                    3: 1,  # Fill-in
                    2: 4  # coding
                }
            questions = []
            for q_type, limit in type_limits.items():
                questions.extend(Questions.fetch_questions_by_type(subunit_id, q_type, limit))

            if not questions:
                return {"error": "No questions found"}, 404

            return questions, 200

        except Exception as e:
            return {"error": str(e)}, 500

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
                    avg_time = q.get("avgTimeSeconds", 120)
                    question = Questions(
                        question_type_id=question_type_id,
                        lesson_id=subunit_id,
                        question_text=q["question"],
                        correct_answer=q["correct_answer"],
                        options=q.get("options", {}),
                        constraints=q.get("constraints", ""),
                        tags=q.get("tags", []),
                        generated=True,
                        skilllevel=skill_level,
                        avgTimeSeconds=avg_time
                    )
                    res = Questions.persist(question)
                    if not res["success"]:
                        raise Exception(res.get("error", "tests error"))
                    question_ids.append(res["data"][0]["questionID"])

            # Generate and persist the questions for each type
            process_questions(json.loads(Prompt.generate_MCQ(prompt)), 1)
            process_questions(json.loads(Prompt.generate_coding(prompt)), 2)
            process_questions(json.loads(Prompt.generate_fill_in(prompt)), 3)
            process_questions(json.loads(Prompt.generate_drag_and_drop(prompt)), 4)

            return {"message": "Questions generated and stored", "question_ids": question_ids}, 200

        except Exception as e:
            return {"error": str(e)}, 500
