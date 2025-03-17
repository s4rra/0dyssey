import json
from typing import List, Optional
from config.settings import supabase_client
import base64
import os
from google import genai
from google.genai import types
from question import *

# Define the SubUnit class
class SubUnit:
    def __init__(self, subUnitID: int, subUnitName: str, subUnitDescription: str, unitID: int, subUnitContent: Optional[dict]):
        self.subUnitID = subUnitID
        self.subUnitName = subUnitName
        self.subUnitDescription = subUnitDescription
        self.unitID = unitID
        self.subUnitContent = subUnitContent  # Can contain learning content

    def __repr__(self):
        return f"SubUnit(subUnitID={self.subUnitID}, Name='{self.subUnitName}', subUnitDescription='{self.subUnitDescription}',unitID='{self.unitID}' )"

# Define the Unit class
class Unit:
    def __init__(self, unitID: int, unitName: str, unitDescription: str, subUnits: List[SubUnit]):
        self.unitID = unitID
        self.unitName = unitName
        self.unitDescription = unitDescription
        self.subUnits = subUnits

    def __repr__(self):
        return f"Unit(ID={self.unitID}, Name='{self.unitName}', SubUnits={len(self.subUnits)}, unitDescription={(self.unitDescription)} )"

class CourseService:
    @staticmethod
    def get_questions():
        try:
            response = (
                supabase_client.table("Question")
                .select("data")
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
        
    def generate_MCQ(prompt):
        try:
            client = genai.Client(
                api_key=os.environ.get("GEMINI_API_KEY2"),
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
                temperature=1,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="application/json",
                system_instruction=[
                    types.Part.from_text(text="""generate 1 NEW python Multiple Choice question based on given input for context
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

    @staticmethod
    def get_courses():
        try:
            response = supabase_client.table("RefUnit").select("*, RefSubUnit(*)").execute()
            ###########
                     
            data = response.data
            #print(f"DATA: {data}")
            # Convert JSON into a list of objects
            units = []
            all_subunits = []

            for unit_data in data:
                unitID = unit_data["unitID"]
                unitName = unit_data["unitName"]
                unitDescription = unit_data["unitDescription"]
                #print(f"UNITDESC ={unitDescription}")
                subUnits = []
                for subunit_data in unit_data["RefSubUnit"]:
                    subUnit = SubUnit(
                        subUnitID=subunit_data["subUnitID"],
                        subUnitName=subunit_data["subUnitName"],
                        subUnitDescription=subunit_data["subUnitDescription"],
                        unitID=subunit_data["unitID"],
                        subUnitContent=subunit_data.get("subUnitContent")  # Might be None
                        )
                    if(subUnit.subUnitID >= 0):
                        prompt = (f"unitDescription:({unitDescription}), subUnitDescription: ({subUnit.subUnitDescription})")
                        print(prompt)
                        theGenQuestion = CourseService.generate_MCQ(prompt)
                        #print(theGenQuestion)
                        theGenQD = json.loads(theGenQuestion)
                        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                        print(theGenQD)
                        
                        question = Question(
                            question_type_id = 1,
                            lesson_id = subUnit.subUnitID,
                            correct_answer = theGenQD["correct_answer"],
                            question_text = theGenQD["question"], 
                            options = theGenQD["options"]
                        )
                        
                        print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
                        response = Question.persist(question)
                        
                        print("=========================================")
                    subUnits.append(subUnit)
                    all_subunits.append(subUnit)
                
                unit = Unit(unitID, unitName, unitDescription, subUnits)
                units.append(unit)

            # Display results
            """  print("All Units:")
            for unit in units:
                print(unit)

            print("\nAll SubUnits:")
            for subunit in all_subunits:
                print(subunit) """

            ###########
        except Exception as e:
            return {"error": str(e)}, 500

courses = CourseService.get_courses()
#print(courses)
#call = CourseService.get_questions()
