import json
from prompt import *
from typing import Optional
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
                    generated: bool):
            
            self.question_type_id = question_type_id
            self.lesson_id = lesson_id
            self.correct_answer = correct_answer
            self.question_text = question_text
            self.options = options
            self.tags = tags
            self.constraints = constraints
            self.generated = generated

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
                        "generated": True
                    }
                ])
                .execute()
            )
            print(response.data)
            return {"success": True, "data": response.data, "status": 201}
        except Exception as exception:
            return {"success": False, "error": str(exception), "status": 500}

    def get_questions(subunit_id, user):
        try:
            skill_level_id = user["chosenSkillLevel"]
            questions = []

            if skill_level_id not in [1, 2, 3]:
                return {"error": "Invalid skill level provided"}, 400

            # Fetch MCQs
            if skill_level_id in [1, 2]:
                limit = 3 if skill_level_id == 1 else 2
                mcq_response = (
                    supabase_client.table("Question")
                    .select("questionID, questionText, correctAnswer, options, questionTypeID")
                    .eq("lessonID", subunit_id)
                    .eq("questionTypeID", 1)
                    .eq("generated", True)
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute()
                )
                if mcq_response.data:
                    questions.extend(mcq_response.data)
            
            # Fetch Fill-in-the-Blank Questions
            if skill_level_id in [1, 2]:
                limit = 3 if skill_level_id == 1 else 2
                fill_in_response = (
                    supabase_client.table("Question")
                    .select("questionID, questionText, correctAnswer, options, questionTypeID")
                    .eq("lessonID", subunit_id)
                    .eq("questionTypeID", 3)  # Fill-in-the-blank
                    .eq("generated", True)
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute()
                )
                if fill_in_response.data:
                    questions.extend(fill_in_response.data)
                
            # Fetch Drag-and-Drop Questions
            if skill_level_id in [1, 2]:
                limit = 2 if skill_level_id == 1 else 3
                drag_and_drop_response = (
                    supabase_client.table("Question")
                    .select("questionID, questionText, correctAnswer, options, questionTypeID")
                    .eq("lessonID", subunit_id)
                    .eq("questionTypeID", 4)  # Drag-and-drop
                    .eq("generated", True)
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute()
                )
                if drag_and_drop_response.data:
                    questions.extend(drag_and_drop_response.data)

            # Fetch Coding
            if skill_level_id in [2, 3]:
                limit = 4 if skill_level_id == 3 else 1
                coding_response = (
                    supabase_client.table("Question")
                    .select("questionID, questionText, correctAnswer, constraints, questionTypeID")
                    .eq("lessonID", subunit_id)
                    .eq("questionTypeID", 2)
                    .eq("generated", True)
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute()
                )
                if coding_response.data:
                    questions.extend(coding_response.data)

            if not questions:
                return {"error": "No questions found"}, 404

            return questions, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def generate_questions(subunit_id):
        try:
            # Fetch subunit info
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
            prompt = f"generate new questions for: unitDescription:({unitDescription}), subUnitDescription: ({subUnitDescription})"
            print(prompt)

            question_ids = []  # Store generated question IDs

            # Generate and store MCQs
            mcq_data = json.loads(Prompt.generate_MCQ(prompt))
            print("=== Generated MCQs ===")
            print(mcq_data)

            for q in mcq_data:
                mcq_store = Questions(
                    question_type_id=1,
                    lesson_id=subunit_id,
                    question_text=q["question"],
                    correct_answer=q["correct_answer"],
                    options=q["options"],
                    constraints="",  # MCQs don't have constraints
                    tags=q["tags"],
                    generated=True
                )
                response = Questions.persist(mcq_store)
                if not response["success"]:
                    return response, response.get("status", 500)
                question_ids.append(response["data"][0]["questionID"])
            
            # Generate and store coding questions
            coding_data = json.loads(Prompt.generate_coding(prompt))
            print("=== Generated Coding Questions ===")
            print(coding_data)

            for q in coding_data:
                coding_store = Questions(
                    question_type_id=2,
                    lesson_id=subunit_id,
                    question_text=q["question"],
                    correct_answer=q["correct_answer"],
                    options={},  # Coding has no options
                    constraints=q["constraints"],
                    tags=q["tags"],
                    generated=True
                )
                response = Questions.persist(coding_store)
                if not response["success"]:
                    return response, response.get("status", 500)
                question_ids.append(response["data"][0]["questionID"])

            # Generate and store fill-in-the-blank questions
            fill_in_data = json.loads(Prompt.generate_fill_in(prompt))
            for q in fill_in_data:
                fill_in_store = Questions(
                    question_type_id=3,
                    lesson_id=subunit_id,
                    question_text=q["question"],
                    correct_answer=q["correct_answer"],
                    options={},
                    constraints="",
                    tags=q["tags"],
                    generated=True
                )
                response = Questions.persist(fill_in_store)
                if not response["success"]:
                    return response, response.get("status", 500)
                question_ids.append(response["data"][0]["questionID"])

            # Generate and store drag-and-drop questions
            drag_and_drop_data = json.loads(Prompt.generate_drag_and_drop(prompt))
            for q in drag_and_drop_data:
                drag_and_drop_store = Questions(
                    question_type_id=4,
                    lesson_id=subunit_id,
                    question_text=q["question"],
                    correct_answer=q["correct_answer"],
                    options=q["options"],
                    constraints="",
                    tags=q["tags"],
                    generated=True
                )
                response = Questions.persist(drag_and_drop_store)
                if not response["success"]:
                    return response, response.get("status", 500)
                question_ids.append(response["data"][0]["questionID"])
                
            return {"message": "Questions generated and stored successfully", "question_ids": question_ids}, 200
        except Exception as e:
            return {"error": str(e)}, 500

#testing
""" if __name__ == "__main__":
    import json

    # Sample test prompt
    prompt = "Unit Description: Understanding how Python stores and processes different types of data.SubUnit Description: Introduces variables, naming rules, and assignment in Python."
    prompt2 = "Unit Description: Using decision-making structures to control program flow. SubUnit Description: Introduces if, elif, and else statements."
    # Call generate
    #raw_response = Questions.generate_MCQ(prompt)
    raw_response = Questions.generate_coding(prompt2)

    # Parse JSON (should be a list of 4 questions)
    try:
        questions = json.loads(raw_response)
        print("\n\n Total Questions Generated:", len(questions))
        for i, q in enumerate(questions, 1):
            print(f"\n Question {i}:")
            print("Q:", q["question"])
            #print("Options:", q["options"])
            print("Constraints:", q["constraints"])
            print("Correct Answer:", q["correct_answer"])
            print("Tags:", q["tags"])
    except Exception as e:
        print("\n failed to parse or print questions:", e)
        print("Raw Response:", raw_response) """
