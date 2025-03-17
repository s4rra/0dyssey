import json
from config.settings import supabase_client
from functions import *

#Handles fetching, AI-based question generation, and answer validation
class QuestionService:
    @staticmethod
    def get_questions(subunit_id, user):
        #fetches questions based on user's skill level and subunit
        try:
            """user_id = user["id"]  # extract userID from session
            
             # Fetch user skill level
            user_response = supabase_client.table("User").select("chosenSkillLevel").eq("userID", user_id).execute()
            if not user_response.data:
                return {"error": "User not found"}, 404
            
            skill_level_id = user_response.data[0]["chosenSkillLevel"] """

            # Fetch questions from the database, based on subunitID and skilllevel
            response = (
                supabase_client.table("Question")
                .select("*")
                .eq("lessonID", 1)
                .limit(5) #ik this will get the first 5 questions that match...
                .execute()
            )
            print(response.data)
            if response.data:
                return response.data, 200
            else:
                return {"error": "No questions found"}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def generate_questions(subunit_id, user):
        # Generates AI-based questions, then attempts to store them in the database
        try:
            user_id = user["id"]  # extract userID from session
            
            # fetch subunit subunit_description
            subunit_response = supabase_client.table("RefSubUnit").select("subUnitDescription").eq("subUnitID", subunit_id).execute()
            if not subunit_response.data:
                return {"error": "Subunit not found"}, 404

            subunit_description = subunit_response.data[0]["subUnitDescription"]

            # fetch user skill level
            user_response = supabase_client.table("User").select("chosenSkillLevel").eq("userID", user_id).execute()
            if not user_response.data:
                return {"error": "User not found"}, 404

            skill_level_id = user_response.data[0]["chosenSkillLevel"]

            # Call AI function to generate questions
            questions = generate_questions(subunit_description, skill_level_id)
            if "error" in questions:
                return questions, 500
            
            # Store generated questions
            return QuestionService.store_generated_questions(questions, skill_level_id, subunit_id)
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def store_generated_questions(questions, skill_level_id, subunit_id):
        #Stores AI-generated questions into the database
        try:
            # Fetch unitID from the subunit table
            unit_response = supabase_client.table("RefSubUnit").select("unitID").eq("subUnitID", subunit_id).execute()
            if not unit_response.data:
                return {"error": "Unit ID not found for subunit"}, 404

            chapter_id = unit_response.data[0]["unitID"]
            
            stored_questions = []

            for question in questions:
                question_type_response = supabase_client.table("questionType").select("questionTypeID").eq("questionType", question["type"]).execute()
                if not question_type_response.data:
                    return {"error": f"Question type '{question['type']}' not found"}, 404
                
                question_type_id = question_type_response.data[0]["questionTypeID"]

                question_data = {
                    "questionTypeID": question_type_id,
                    "skillLevelID": skill_level_id,
                    "lessonID": subunit_id,
                    "chapterID": chapter_id,
                    "questionText": question["question"],
                    "generated": True,
                    "options": json.dumps(question.get("options", {})),  # Store options as JSON
                    "correctAnswer": question.get("correct_answer", ""),  # Store correct answer directly in question
                    "dropdowns": json.dumps(question.get("dropdowns", [])),  # Store dropdowns as JSON
                    "expected_output": question.get("expected_output", ""),  # For coding questions
                    "constraints": question.get("constraints", "")  # For coding questions
                }

                question_response = supabase_client.table("Question").insert(question_data).execute()
                if question_response.data:
                    stored_questions.append(question_response.data[0])

            return {"message": "Questions stored successfully", "questions": stored_questions}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def check_answers(user, user_answers):
        try:
            user_id = user["id"]  # extract userID from session
            
            # Fetch questions with their correct answers
            question_ids = list(user_answers.keys())
            questions_response = supabase_client.table("Question").select("questionID, correctAnswer, questionTypeID, expected_output, constraints").in_("questionID", question_ids).execute()
            
            if not questions_response.data:
                return {"error": "No questions found"}, 404

            # Group questions by ID for easy lookup
            questions = {str(q["questionID"]): q for q in questions_response.data}
            
            # Calculate score
            score = 0
            results = []
            
            for q_id, answer in user_answers.items():
                if q_id in questions:
                    question = questions[q_id]
                    is_correct = False
                    
                    # Check if it's a coding question (call check_code)
                    question_type_response = supabase_client.table("questionType").select("questionType").eq("questionTypeID", question["questionTypeID"]).execute()
                    if question_type_response.data and question_type_response.data[0]["questionType"] == "coding":
                        # Use the check_code function for coding questions
                        code_check = check_code(answer, question["expected_output"], question["constraints"])
                        # Determine if the code is correct based on the AI's evaluation
                        is_correct = "correct" in code_check.get("feedback", "").lower()
                    else:
                        # Simple comparison for most question types
                        if answer == question["correctAnswer"]:
                            is_correct = True
                    
                    if is_correct:
                        score += 1
                    
                    results.append({
                        "questionID": q_id,
                        "correct": is_correct
                    })

            # Update user points
            supabase_client.table("User").update({"Points": supabase_client.sql("Points + " + str(score))}).eq("userID", user_id).execute()

            return {"score": score, "total": len(user_answers), "results": results}, 200
        except Exception as e:
            return {"error": str(e)}, 500
        
response =QuestionService.get_questions(1,"")