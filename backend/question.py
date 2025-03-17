from test import *
from config.settings import supabase_client

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
            )
            print(response.data)
            return response
        except Exception as exception:
            return exception

        
        

