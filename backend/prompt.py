import base64
import os
import json
from typing import List, Optional
from google import genai
from google.genai import types
from config.settings import supabase_client
from services.user_service import UserService

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
                temperature=0.3,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
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
                system_instruction=[
                    types.Part.from_text(text="""Act as an energetic and engaging teacher creating 1 unique Python question for students aged 10–17. Your goal is to generate structured question strictly based on the provided context. 
                    Make sure the question is directly related to the subunit description. Keep it fun, educational, and clear!"""),
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
                temperature=0.3,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
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
                system_instruction=[
                    types.Part.from_text(text="""Act as an energetic and engaging teacher creating 1 unique Python question for students aged 10–17. Your goal is to generate structured question strictly based on the provided context. 
                    Make sure the question is directly related to the subunit description. Keep it fun, educational, and clear!"""),
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

    def check_coding(input):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=input),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=0,
                top_p=1,
                top_k=40,
                max_output_tokens=500,
                response_mime_type="application/json",
                response_schema=genai.types.Schema(
                    type = genai.types.Type.OBJECT,
                    required = ["questionid", "user_answer", "hint", "feedback"],
                    properties = {
                        "questionid": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "ID that links this feedback to the original question",
                        ),
                        "user_answer": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "The student's submitted code or answer",
                        ),
                        "hint": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "A Socratic-style hint that nudges the student to think deeper without revealing the answer",
                        ),
                        "feedback": genai.types.Schema(
                            type = genai.types.Type.STRING,
                            description = "Encouraging, constructive feedback with high-level suggestions or questions",
                        ),
                    },
                ),
                system_instruction=[
                    types.Part.from_text(text="""You are a Python tutor analyzing student answers for multiple Python coding questions for students aged 10–17.
                    Your task is to:
                    Compare the user’s answer with the expected output and any provided constraints
                    Identify errors: Highlight syntax mistakes, logic errors, or violations of the constraints
                    Provide hints: Offer a Socratic-style hint that points out where the issue may lie, without revealing the solution. Avoid naming specific functions or methods
                    Analyze efficiency: Comment on whether the solution could be improved (if applicable)
                    Give feedback: Encourage correct answers with reinforcement, and provide constructive feedback if incorrect by guiding the student toward discovery using a relatable example or question
                    Your response must follow the structured output format and stay within the scope of the student’s input.
                    expected input:
                    {
                    \"questionid\": \"\",
                    \"question\": \"\",
                    \"correct_answer\": \"expected output\",
                    \"constraints\": \"\",
                    \"user_answer\": \"\"
                    }"""),
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
            "error": "Failed to analyze student's coding answer",
            "details": str(e),
            "status": 500
        }
        
    def get_questions(subunit_id, user):
        try:
            #user_id = user["id"]  # extract userID from session
            
            # Fetch user skill level from session
            if "chosenSkillLevel" not in user:
               return {"error": "Skill level not provided in user session"}, 400

            skill_level_id = user["chosenSkillLevel"]

            # Determine question types to fetch based on skill level
            if skill_level_id == 1:
                question_type = [1]  # Only MCQ (for now)
            elif skill_level_id == 2:
                question_type = [1, 2]  # Both MCQ and Coding (for now)
            elif skill_level_id == 3:
                question_type = [2]  # Only Coding
            else:
                return {"error": "Invalid skill level provided"}, 400
            
            # Fetch questions that match the user's skill level and lesson
            response = (
                supabase_client.table("Question")
                .select("*")
                .eq("lessonID", subunit_id)
                .in_("questionTypeID", question_type)
                .execute()
            )
            
            if response.data:
                print(response.data)
                return response.data, 200
            else:
                return {"error": "No questions found for this skill level"}, 404
        except Exception as e:
            return {"error": str(e)}, 500
    
    def generate_questions(subunit_id, user):
        try:
            user_profile, status = UserService.get_user_profile(user)
            if status != 200:
                return user_profile, status  
            
            unitDescription = user_profile["RefUnit"]["unitDescription"]
            subUnitDescription = user_profile["RefSubUnit"]["subUnitDescription"]

            prompt = f"generate new questions for: unitDescription:({unitDescription}), subUnitDescription: ({subUnitDescription})"
            print(prompt)

            question_ids = []  # Store generated question IDs

            # Generate and store MCQ
            theGenQuestion = Questions.generate_MCQ(prompt)
            theGenQD = json.loads(theGenQuestion)
            print("===================================")
            print(theGenQD)

            mcq_store = Questions(
                question_type_id=1,
                lesson_id=subunit_id,
                question_text=theGenQD["question"],
                correct_answer=theGenQD["correct_answer"],
                options=theGenQD["options"],
                constraints="", 
                tags=theGenQD["tags"],
                generated=True
            )
            mcq_response = Questions.persist(mcq_store)
            if not mcq_response["success"]:
                return mcq_response, mcq_response.get("status", 500)
            question_ids.append(mcq_response["data"][0]["questionID"]) # store generated MCQ ID
 
            theGenCodingQuestion = Questions.generate_coding(prompt)
            theGencodingD = json.loads(theGenCodingQuestion)
            print("==================================")
            print(theGencodingD)

            coding_store = Questions(
                question_type_id=2,
                lesson_id=subunit_id,
                question_text=theGencodingD["question"],
                correct_answer=theGencodingD["correct_answer"],
                options={},
                constraints=theGencodingD["constraints"],
                tags=theGencodingD["tags"],
                generated=True
            )
            coding_response = Questions.persist(coding_store)
            if not coding_response["success"]:
                return coding_response, coding_response.get("status", 500)
            question_ids.append(coding_response["data"][0]["questionID"])# store generated Coding ID

            return {"message": "Questions generated and stored successfully", "question_ids": question_ids}, 200
        except Exception as e:
            return {"error": str(e)}, 500
