from supabase import create_client, Client
from datetime import datetime

url = "your_supabase_url"
key = "your_supabase_key"
supabase: Client = create_client(url, key)

class Answer:
    def __init__(self, answerID=None, questionID=None, is_correct=False, userID=None,
                 userAnswer="", correctAnswer="", feedback=None, hint=None, Points=None,
                 retry=None, startedAt=None, completedAt=None, timeTaken=None):
        self._answerID = answerID
        self._questionID = questionID
        self._is_correct = is_correct
        self._userID = userID
        self._userAnswer = userAnswer
        self._correctAnswer = correctAnswer
        self._feedback = feedback
        self._hint = hint
        self._Points = Points
        self._retry = retry
        self._startedAt = startedAt
        self._completedAt = completedAt
        self._timeTaken = timeTaken

    # 🧠 Getters & Setters
    def get_answerID(self): return self._answerID
    def set_answerID(self, val): self._answerID = val

    def get_questionID(self): return self._questionID
    def set_questionID(self, val): self._questionID = val

    def get_is_correct(self): return self._is_correct
    def set_is_correct(self, val): self._is_correct = val

    def get_userID(self): return self._userID
    def set_userID(self, val): self._userID = val

    def get_userAnswer(self): return self._userAnswer
    def set_userAnswer(self, val): self._userAnswer = val

    def get_correctAnswer(self): return self._correctAnswer
    def set_correctAnswer(self, val): self._correctAnswer = val

    def get_feedback(self): return self._feedback
    def set_feedback(self, val): self._feedback = val

    def get_hint(self): return self._hint
    def set_hint(self, val): self._hint = val

    def get_Points(self): return self._Points
    def set_Points(self, val): self._Points = val

    def get_retry(self): return self._retry
    def set_retry(self, val): self._retry = val

    def get_startedAt(self): return self._startedAt
    def set_startedAt(self, val): self._startedAt = val

    def get_completedAt(self): return self._completedAt
    def set_completedAt(self, val): self._completedAt = val

    def get_timeTaken(self): return self._timeTaken
    def set_timeTaken(self, val): self._timeTaken = val

    # 💾 Save to DB
    def persist_to_db(self):
        data = {
            "questionID": self._questionID,
            "is_correct": self._is_correct,
            "userID": self._userID,
            "userAnswer": self._userAnswer,
            "correctAnswer": self._correctAnswer,
            "feedback": self._feedback,
            "hint": self._hint,
            "Points": self._Points,
            "retry": self._retry,
            "startedAt": self._startedAt,
            "completedAt": self._completedAt,
            "timeTaken": self._timeTaken
        }
        res = supabase.table("Answer").insert(data).execute()
        return res

    # 🔍 Fetch from DB
    @staticmethod
    def from_db(answerID):
        res = supabase.table("Answer").select("*").eq("answerID", answerID).single().execute()
        if res.data:
            return Answer(**res.data)
        return None
