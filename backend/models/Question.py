from supabase import create_client, Client
from datetime import datetime

url = "your_supabase_url"
key = "your_supabase_key"
supabase: Client = create_client(url, key)

class Question:
    def __init__(self, questionID=None, questionTypeID=None, lessonID=None, generated=False,
                 tags=None, correctAnswer="", questionText="", options=None,
                 constraints=None, created_at=None, skilllevel=None, avgTimeSeconds=None):
        self._questionID = questionID
        self._questionTypeID = questionTypeID
        self._lessonID = lessonID
        self._generated = generated
        self._tags = tags
        self._correctAnswer = correctAnswer
        self._questionText = questionText
        self._options = options
        self._constraints = constraints
        self._created_at = created_at or datetime.utcnow().isoformat()
        self._skilllevel = skilllevel
        self._avgTimeSeconds = avgTimeSeconds

    # ✨ Getters & Setters
    def get_questionID(self): return self._questionID
    def set_questionID(self, val): self._questionID = val

    def get_questionTypeID(self): return self._questionTypeID
    def set_questionTypeID(self, val): self._questionTypeID = val

    def get_lessonID(self): return self._lessonID
    def set_lessonID(self, val): self._lessonID = val

    def get_generated(self): return self._generated
    def set_generated(self, val): self._generated = val

    def get_tags(self): return self._tags
    def set_tags(self, val): self._tags = val

    def get_correctAnswer(self): return self._correctAnswer
    def set_correctAnswer(self, val): self._correctAnswer = val

    def get_questionText(self): return self._questionText
    def set_questionText(self, val): self._questionText = val

    def get_options(self): return self._options
    def set_options(self, val): self._options = val

    def get_constraints(self): return self._constraints
    def set_constraints(self, val): self._constraints = val

    def get_created_at(self): return self._created_at
    def set_created_at(self, val): self._created_at = val

    def get_skilllevel(self): return self._skilllevel
    def set_skilllevel(self, val): self._skilllevel = val

    def get_avgTimeSeconds(self): return self._avgTimeSeconds
    def set_avgTimeSeconds(self, val): self._avgTimeSeconds = val

    # 💾 Save to DB
    def persist_to_db(self):
        data = {
            "questionTypeID": self._questionTypeID,
            "lessonID": self._lessonID,
            "generated": self._generated,
            "tags": self._tags,
            "correctAnswer": self._correctAnswer,
            "questionText": self._questionText,
            "options": self._options,
            "constraints": self._constraints,
            "created_at": self._created_at,
            "skilllevel": self._skilllevel,
            "avgTimeSeconds": self._avgTimeSeconds
        }
        res = supabase.table("Question").insert(data).execute()
        return res

    # 🔍 Fetch from DB
    @staticmethod
    def from_db(questionID):
        res = supabase.table("Question").select("*").eq("questionID", questionID).single().execute()
        if res.data:
            return Question(**res.data)
        return None
