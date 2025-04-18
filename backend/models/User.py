from supabase import create_client, Client
from datetime import datetime

# ⚙️ Replace with your own Supabase credentials
url = "your_supabase_url"
key = "your_supabase_key"
supabase: Client = create_client(url, key)

class User:
    def __init__(self, userName, chosenSkillLevel, DOB=None, points=0, streakLength=0,
                 currentUnit=0, currentSubUnit=0, userID=None, Email="", Password="",
                 lastLogin=None, profilePicture=None):
        self._userName = userName
        self._chosenSkillLevel = chosenSkillLevel
        self._DOB = DOB
        self._points = points
        self._streakLength = streakLength
        self._currentUnit = currentUnit
        self._currentSubUnit = currentSubUnit
        self._userID = userID
        self._Email = Email
        self._Password = Password
        self._lastLogin = lastLogin
        self._profilePicture = profilePicture

    # 📥 Getters & Setters
    def get_userName(self): return self._userName
    def set_userName(self, val): self._userName = val

    def get_chosenSkillLevel(self): return self._chosenSkillLevel
    def set_chosenSkillLevel(self, val): self._chosenSkillLevel = val

    def get_DOB(self): return self._DOB
    def set_DOB(self, val): self._DOB = val

    def get_points(self): return self._points
    def set_points(self, val): self._points = val

    def get_streakLength(self): return self._streakLength
    def set_streakLength(self, val): self._streakLength = val

    def get_currentUnit(self): return self._currentUnit
    def set_currentUnit(self, val): self._currentUnit = val

    def get_currentSubUnit(self): return self._currentSubUnit
    def set_currentSubUnit(self, val): self._currentSubUnit = val

    def get_userID(self): return self._userID
    def set_userID(self, val): self._userID = val

    def get_Email(self): return self._Email
    def set_Email(self, val): self._Email = val

    def get_Password(self): return self._Password
    def set_Password(self, val): self._Password = val

    def get_lastLogin(self): return self._lastLogin
    def set_lastLogin(self, val): self._lastLogin = val

    def get_profilePicture(self): return self._profilePicture
    def set_profilePicture(self, val): self._profilePicture = val

    # 💾 Save to DB
    def persist_to_db(self):
        data = {
            "userName": self._userName,
            "chosenSkillLevel": self._chosenSkillLevel,
            "DOB": self._DOB,
            "points": self._points,
            "streakLength": self._streakLength,
            "currentUnit": self._currentUnit,
            "currentSubUnit": self._currentSubUnit,
            "userID": self._userID,  # Optional – Supabase might auto-generate
            "Email": self._Email,
            "Password": self._Password,
            "lastLogin": self._lastLogin,
            "profilePicture": self._profilePicture
        }
        res = supabase.table("User").insert(data).execute()
        return res

    # 🔍 Load from DB
    @staticmethod
    def from_db(userID):
        res = supabase.table("User").select("*").eq("userID", userID).single().execute()
        if res.data:
            return User(
                userName=res.data["userName"],
                chosenSkillLevel=res.data["chosenSkillLevel"],
                DOB=res.data.get("DOB"),
                points=res.data["points"],
                streakLength=res.data["streakLength"],
                currentUnit=res.data.get("currentUnit", 0),
                currentSubUnit=res.data.get("currentSubUnit", 0),
                userID=res.data["userID"],
                Email=res.data["Email"],
                Password=res.data["Password"],
                lastLogin=res.data.get("lastLogin"),
                profilePicture=res.data.get("profilePicture")
            )
        return None
