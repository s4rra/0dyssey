import base64
import os
import json
from typing import Optional
from google import genai
from google.genai import types
from config.settings import supabase_client
from services.user_service import *

#QuestionService fixing
class SubUnit:
    def __init__(self, subUnitID: int, subUnitName: str, subUnitDescription: str, unitID: int, subUnitContent: Optional[dict]):
        self.subUnitID = subUnitID
        self.subUnitName = subUnitName
        self.subUnitDescription = subUnitDescription
        self.unitID = unitID
        self.subUnitContent = subUnitContent  

    def __repr__(self):
        return f"SubUnit(subUnitID={self.subUnitID}, Name='{self.subUnitName}', subUnitDescription='{self.subUnitDescription}',unitID='{self.unitID}' )"

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
            return {"success": True, "data": response.data}
        except Exception as exception:
            return {"success": False, "error": str(exception), "status": 500}

    def generate_MCQ(prompt):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0.5,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["question", "options", "correct_answer", "tags"],
                        properties = {
                            "question": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "options": genai.types.Schema(
                                type = genai.types.Type.OBJECT,
                                required = ["a", "b", "c", "d"],
                                properties = {
                                    "a": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "b": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "c": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                    "d": genai.types.Schema(
                                        type = genai.types.Type.STRING,
                                    ),
                                },
                            ),
                            "correct_answer": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "tags": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                        },
                    ),
                ),
                system_instruction=[
                    types.Part.from_text(text="""Act as an energetic and engaging teacher creating 4 unique Python multiple-choice questions in a JSON array,
                                         each question must follow the schema exactly. Respond with a JSON array only. Make questions educational, age-appropriate (10–17),
                                         fun, and directly tied to the provided subunit description! Avoid repeating the same question with slight rewording"""),],
            )

            response = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text
            return response
        except Exception as e:
            return {
            "error": "Failed to generate MCQ",
            "details": str(e),
            "status": 500
        }
            
    def generate_coding(prompt):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0.5,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["question", "correct_answer", "constraints", "tags"],
                        properties = {
                            "question": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "correct_answer": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "constraints": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "tags": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                        },
                    ),
                ),
                system_instruction=[
                    types.Part.from_text(text="""Act as an energetic and engaging teacher creating 4 Python short coding questions
                                         in a JSON array. Follow the schema exactly. Each question must ask the student to write code, not a full program.
                                         Stick to the subunit description content scope ONLY. Keep it educational, age-appropriate (10–17), and fun. 
                                         Avoid repeating the same question with slight rewording!"""),
                ],
            )

            response = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text
            return response
        except Exception as e:
            return {
            "error": "Failed to generate coding question",
            "details": str(e),
            "status": 500
        }

    def get_questions(subunit_id, user):
        try:
            skill_level_id = user["chosenSkillLevel"]
            questions = []

            if skill_level_id not in [1, 2, 3]:
                return {"error": "Invalid skill level provided"}, 400

            # Fetch MCQs
            if skill_level_id in [1, 2]:
                limit = 4 if skill_level_id == 1 else 2
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

            # Fetch Coding
            if skill_level_id in [2, 3]:
                limit = 4 if skill_level_id == 3 else 2
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

    def generate_questions(subunit_id, user):
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
            mcq_data = json.loads(Questions.generate_MCQ(prompt))
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
            coding_data = json.loads(Questions.generate_coding(prompt))
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
