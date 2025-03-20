import json
from typing import List, Optional
from config.settings import supabase_client
import base64
import os
from google import genai
from google.genai import types
import random
import time
#this file is a testing file
class SubUnit:
    def __init__(self, subUnitID: int, subUnitName: str, subUnitDescription: str, unitID: int, subUnitContent: Optional[dict]):
        self.subUnitID = subUnitID
        self.subUnitName = subUnitName
        self.subUnitDescription = subUnitDescription
        self.unitID = unitID
        self.subUnitContent = subUnitContent  

    def __repr__(self):
        return f"SubUnit(subUnitID={self.subUnitID}, Name='{self.subUnitName}', subUnitDescription='{self.subUnitDescription}',unitID='{self.unitID}' )"


class Question:
    def __init__(self,
                 question_type_id: int,
                 lesson_id: int,
                 correct_answer: str,
                 question_text: str, 
                 options: dict ):
        self.question_type_id = question_type_id
        self.lesson_id = lesson_id
        self.correct_answer = correct_answer
        self.question_text = question_text
        self.options = options
        
    def persist(question):
        try:
            
            response = (
                supabase_client.table("Question")
                .insert([
                    {   
                        "questionTypeID":question.question_type_id,
                        "lessonID": question.lesson_id,
                        "questionText": question.question_text,
                        "correctAnswer": question.correct_answer,
                        "options": question.options,
                        "generated": True
                    }
                ])
                .execute()
                .cache_control("no-cache") 
            )
            print(response.data)
            return response
        except Exception as exception:
            return exception
        
    def generate_MCQ(prompt):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY"),
            )

            model = "gemini-2.0-flash"
            # Add "unique identifier to force different responses"
            random_token = random.randint(1000, 9999)
            unique_prompt = f"{prompt} (RandomID: {random_token}, Timestamp: {time.time()})"
            
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=unique_prompt),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                top_p=0.8,
                top_k=50,
                max_output_tokens=8192,
                response_mime_type="application/json",
                system_instruction=[
                    types.Part.from_text(text="""generate 1 unique python Multiple Choice question based on given input for context
                    output json format example:
                    {
                            "question": "question text",
                            "options": {
                                "a": "option1",
                                "b": "option2",
                                "c": "option3",
                                "d": "option4"
                            },
                            "correct_answer": "correct answer"
                    }
                    """),
                ],
            )
            response = ""  # Initialize empty string to store the full response
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ): 
                print(chunk.text, end="")
                response += chunk.text  # Append each chunk to the response
            
            return response # Return the complete response after streaming ends
        except Exception as e:
            return {"error": str(e), "status": 500}

    def questions():
        try:
            response = (
                supabase_client
                .table("RefSubUnit")
                .select("*, RefUnit(unitDescription)")
                .order("subUnitID")
                .execute()
                )
            
            data = response.data
            #print(f"DATA: {data}")
            subUnits = []
            for subunit_data in data:
                unitDescription = subunit_data["RefUnit"]["unitDescription"]
                subUnits.append(unitDescription)
                print(f"UNITDESC ={unitDescription}")
                subUnit = SubUnit(
                    subUnitID=subunit_data["subUnitID"],
                    subUnitName=subunit_data["subUnitName"],
                    subUnitDescription=subunit_data["subUnitDescription"],
                    unitID=subunit_data["unitID"],
                    subUnitContent=subunit_data.get("subUnitContent") 
                    )
                subUnits.append(subUnit)
                if(subUnit.subUnitID <= 4):
                    prompt = (f"unitDescription:({unitDescription}), subUnitDescription: ({subUnit.subUnitDescription}), subUnitID: ({subUnit.subUnitID})")
                    print(prompt)
                    theGenQuestion = Question.generate_MCQ(prompt)
                    #print(theGenQuestion)
                    theGenQD = json.loads(theGenQuestion)
                    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                    print(theGenQD)
                    
                    store = Question(
                            question_type_id = 1,
                            lesson_id = subUnit.subUnitID,
                            question_text = theGenQD["question"],
                            correct_answer = theGenQD["correct_answer"],
                            options = theGenQD["options"]
                        )
                    
                    print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
                    response = Question.persist(store)
                    
                    print("=========================================")
                
            # Display results
            """ print("\nAll SubUnits:")
            for subunit in subUnits:
                print(subunit) """
        except Exception as e:
            return {"error": str(e)}, 500

courses = Question.questions()
#print(courses)
#call = CourseService.get_questions()

        
        

