from datetime import datetime, timezone
import json
from config.settings import supabase_client

class MissionService:
    @staticmethod
    def get_missions(user_id):
        """
        Get available missions with completion status.
        """
        try:
            # Build the query - now including imageUrl
            query = supabase_client.from_("Missions").select(
                "missionID, missionTitle, missionDescription, difficulty, xpReward, imageUrl, createdAt"
            )
            
            # Execute query
            missions_response = query.execute()
            
            if not missions_response.data:
                return {"missions": []}, 200
            
            missions = missions_response.data
            
            # Fetch user progress for these missions
            mission_ids = [mission["missionID"] for mission in missions]
            progress_response = supabase_client.from_("UserMissionProgress") \
                .select("missionID, completed, score") \
                .eq("userID", user_id) \
                .in_("missionID", mission_ids) \
                .execute()
            
            # Create a lookup dictionary for quick access
            progress_lookup = {
                item["missionID"]: {"completed": item["completed"], "score": item["score"]} 
                for item in progress_response.data
            }
            
            # Enrich missions with progress data
            for mission in missions:
                mission_id = mission["missionID"]
                if mission_id in progress_lookup:
                    mission["completed"] = progress_lookup[mission_id]["completed"]
                    mission["score"] = progress_lookup[mission_id]["score"]
                else:
                    mission["completed"] = False
                    mission["score"] = 0
            
            return {"missions": missions}, 200
            
        except Exception as e:
            print(f"Error fetching missions: {e}")
            return {"error": str(e)}, 500

    @staticmethod
    def get_mission_details(user_id, mission_id):
        """
        Get detailed mission information including chapters with stories and questions.
        For completed missions, also includes user's previous answers.
        """
        try:
            # Get mission details - using .eq() instead of .single() to handle empty results better
            # Now including imageUrl field
            mission_response = supabase_client.from_("Missions") \
                .select("*") \
                .eq("missionID", mission_id) \
                .execute()
            
            # Check if we got any results
            if not mission_response.data or len(mission_response.data) == 0:
                return {"error": "Mission not found"}, 404
            
            # Get the first (and should be only) result
            mission = mission_response.data[0]
            
            # Debug: Print mission content structure
            print(f"Mission content structure: {type(mission.get('content'))}")
            if isinstance(mission.get('content'), dict):
                print(f"Content keys: {mission.get('content').keys()}")
            
            # Check if user has already completed this mission
            progress_response = supabase_client.from_("UserMissionProgress") \
                .select("completed, score, answers") \
                .eq("userID", user_id) \
                .eq("missionID", mission_id) \
                .execute()
            
            # Process content based on actual DB structure
            content = mission.get("content", {})
            
            # Check if content has the expected structure
            if not content or not isinstance(content, dict):
                print(f"Content is not a dict: {type(content)}")
                # Try to parse content if it's a string
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                        print("Successfully parsed content JSON string")
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse content: {e}")
                        return {"error": "Invalid mission content structure"}, 500
                else:
                    return {"error": "Invalid mission content structure"}, 500
                
            chapters = content.get("chapters", [])
            print(f"Chapters type: {type(chapters)}, length: {len(chapters)}")
            
            processed_chapters = []
            
            # If user hasn't completed the mission, remove correct answers
            is_completed = False
            user_answers = None
            user_score = 0
            
            if progress_response.data and len(progress_response.data) > 0:
                user_progress = progress_response.data[0]
                is_completed = user_progress.get("completed", False)
                user_answers = user_progress.get("answers")
                user_score = user_progress.get("score", 0)
            
            # Process each chapter
            for chapter in chapters:
                print(f"Processing chapter: {type(chapter)}")
                if isinstance(chapter, str):
                    try:
                        chapter = json.loads(chapter)
                        print("Successfully parsed chapter JSON string")
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse chapter: {e}")
                        continue
                
                chapter_copy = chapter.copy()
                processed_questions = []
                
                # Debug: Print chapter structure
                print(f"Chapter keys: {chapter_copy.keys() if isinstance(chapter_copy, dict) else 'Not a dict'}")
                
                # Process each question in this chapter
                questions = chapter.get("questions", [])
                print(f"Questions type: {type(questions)}, length: {len(questions)}")
                
                for question in questions:
                    print(f"Processing question: {type(question)}")
                    if isinstance(question, str):
                        try:
                            question = json.loads(question)
                            print("Successfully parsed question JSON string")
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse question: {e}")
                            continue
                    
                    question_copy = question.copy()
                    
                    # Debug: Print question structure
                    print(f"Question type: {question_copy.get('type')}")
                    if question_copy.get('type') == 'mcq':
                        print(f"MCQ options type: {type(question_copy.get('options'))}")
                        for i, opt in enumerate(question_copy.get('options', [])):
                            print(f"Option {i} type: {type(opt)}")
                    
                    # If not completed, don't send correct answers to frontend
                    if not is_completed:
                        if question_copy.get("type") == "mcq":
                            # In your DB, the answer is stored directly 
                            if "answer" in question_copy:
                                answer_value = question_copy["answer"]
                                del question_copy["answer"]
                                
                                # Add isCorrect field to options for consistency with frontend
                                options = question_copy.get("options", [])
                                for i, option in enumerate(options):
                                    # Make sure option is a dictionary before assignment
                                    if isinstance(option, dict):
                                        option["isCorrect"] = (option.get("id") == answer_value)
                                    # If option is a string, we need a different approach
                                    elif isinstance(option, str):
                                        # Convert string options to dicts with isCorrect attribute
                                        options[i] = {
                                            "text": option,
                                            "id": option,
                                            "isCorrect": (option == answer_value)
                                        }
                        
                        elif question_copy.get("type") == "dragdrop":
                            # For drag and drop questions, adapt structure if needed
                            if "answers" in question_copy:
                                # Create a correctPlacements dict that maps blanks to answers
                                blanks = question_copy.get("blanks", [])
                                answers = question_copy.get("answers", [])
                                
                                # Create correctPlacements mapping (then remove it for frontend)
                                correct_placements = {}
                                for i, blank in enumerate(blanks):
                                    if i < len(answers):
                                        correct_placements[blank] = answers[i]
                                
                                question_copy["correctPlacements"] = correct_placements
                                
                                # Remove answers if not completed
                                if not is_completed:
                                    del question_copy["answers"]
                                    if "correctPlacements" in question_copy:
                                        del question_copy["correctPlacements"]
                    
                    # Fix the questionText field if needed
                    if "questionText" not in question_copy and "question" in question_copy:
                        question_copy["questionText"] = question_copy["question"]
                    
                    processed_questions.append(question_copy)
                
                # Replace questions with processed questions
                chapter_copy["questions"] = processed_questions
                processed_chapters.append(chapter_copy)
            
            response_data = {
                "missionID": mission["missionID"],
                "missionTitle": mission["missionTitle"],
                "missionDescription": mission["missionDescription"],
                "difficulty": mission["difficulty"],
                "xpReward": mission["xpReward"],
                "imageUrl": mission.get("imageUrl"),  # Add mission image URL
                "content": {
                    "chapters": processed_chapters
                },
                "completed": is_completed,
                "score": user_score
            }
            
            # Include user's previous answers if available
            if user_answers:
                response_data["userAnswers"] = user_answers
            
            return response_data, 200
            
        except Exception as e:
            print(f"Error fetching mission details: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}, 500

    # The rest of your MissionService class remains unchanged...
    @staticmethod
    def submit_answers(user_id, mission_id, user_answers):
        """
        Submit and evaluate mission answers.
        Updates user progress and rewards XP.
        """
        try:
            # Get mission details with correct answers - using .eq() instead of .single()
            mission_response = supabase_client.from_("Missions") \
                .select("*") \
                .eq("missionID", mission_id) \
                .execute()
            
            if not mission_response.data or len(mission_response.data) == 0:
                return {"error": "Mission not found"}, 404
            
            mission = mission_response.data[0]
            content = mission["content"]
            
            # Adjust for actual DB structure - collect questions from all chapters
            all_questions = []
            for chapter in content.get("chapters", []):
                all_questions.extend(chapter.get("questions", []))
            
            # Check if mission is already completed
            progress_response = supabase_client.from_("UserMissionProgress") \
                .select("completed") \
                .eq("userID", user_id) \
                .eq("missionID", mission_id) \
                .execute()
            
            already_completed = False
            if progress_response.data and len(progress_response.data) > 0:
                already_completed = progress_response.data[0].get("completed", False)
            
            # Calculate score based on correct answers
            total_questions = len(all_questions)
            correct_answers = 0
            
            for i, question in enumerate(all_questions):
                if i >= len(user_answers):
                    continue  # Skip if user didn't answer this question
                
                user_answer = user_answers[i]
                
                if question["type"] == "mcq":
                    # For MCQ, check if selected option matches the correct answer
                    correct_answer = question.get("answer")
                    
                    # Handle different ways user_answer might be provided
                    if isinstance(user_answer, str):
                        # Direct string comparison
                        if user_answer == correct_answer:
                            correct_answers += 1
                    elif isinstance(user_answer, dict) and "id" in user_answer:
                        # If user_answer is a dict with id key
                        if user_answer["id"] == correct_answer:
                            correct_answers += 1
                
                elif question["type"] == "dragdrop":
                    # For drag and drop, check if placements match
                    correct_answers_list = question.get("answers", [])
                    blanks = question.get("blanks", [])
                    
                    # Modified approach for drag and drop validation
                    # Only check the blanks that the user has filled
                    if isinstance(user_answer, dict):
                        correct_placements = 0
                        total_filled = 0
                        
                        # Check each blank that user has filled
                        for blank_idx, blank in enumerate(blanks):
                            if blank in user_answer and blank_idx < len(correct_answers_list):
                                total_filled += 1
                                if user_answer[blank] == correct_answers_list[blank_idx]:
                                    correct_placements += 1
                        
                        # Consider the question correct if all filled blanks are correct
                        if total_filled > 0 and correct_placements == total_filled:
                            correct_answers += 1
            
            # Calculate score as percentage
            score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
            is_completed = score >= 70  # Consider mission completed if score is 70% or higher
            
            # Update or insert progress record
            progress_data = {
                "userID": user_id,
                "missionID": mission_id,
                "completed": is_completed,
                "score": score,
                "answers": user_answers,
                "completedAt": datetime.now(timezone.utc).isoformat() if is_completed else None
            }
            
            if progress_response.data and len(progress_response.data) > 0:
                # Update existing record
                supabase_client.from_("UserMissionProgress") \
                    .update(progress_data) \
                    .eq("userID", user_id) \
                    .eq("missionID", mission_id) \
                    .execute()
            else:
                # Insert new record
                supabase_client.from_("UserMissionProgress") \
                    .insert(progress_data) \
                    .execute()
            
            # Award XP points if mission is completed for the first time
            if is_completed and not already_completed:
                # Get current user points
                user_response = supabase_client.from_("User") \
                    .select("points") \
                    .eq("userID", user_id) \
                    .execute()
                
                if user_response.data and len(user_response.data) > 0:
                    current_points = user_response.data[0].get("points", 0)
                    new_points = current_points + mission["xpReward"]
                    
                    # Update user points
                    supabase_client.from_("User") \
                        .update({"points": new_points}) \
                        .eq("userID", user_id) \
                        .execute()
            
            # Return results
            result = {
                "success": True,
                "score": score,
                "completed": is_completed,
                "correctAnswers": correct_answers,
                "totalQuestions": total_questions
            }
            
            if is_completed and not already_completed:
                result["xpAwarded"] = mission["xpReward"]
            
            return result, 200
            
        except Exception as e:
            print(f"Error submitting mission answers: {e}")
            return {"error": str(e)}, 500

    @staticmethod
    def get_user_progress(user_id):
        """
        Get user's progress across all missions.
        """
        try:
            progress_response = supabase_client.from_("UserMissionProgress") \
                .select("*, Missions(missionID, missionTitle, imageUrl)") \
                .eq("userID", user_id) \
                .execute()
            
            if not progress_response.data:
                return {"missions": []}, 200
            
            # Process the response
            missions_progress = []
            for progress in progress_response.data:
                mission_info = progress["Missions"]
                missions_progress.append({
                    "missionID": mission_info["missionID"],
                    "missionTitle": mission_info["missionTitle"],
                    "imageUrl": mission_info.get("imageUrl"),  # Include image URL
                    "completed": progress["completed"],
                    "score": progress["score"],
                    "completedAt": progress["completedAt"]
                })
            
            return {"missions": missions_progress}, 200
            
        except Exception as e:
            print(f"Error fetching user mission progress: {e}")
            return {"error": str(e)}, 500