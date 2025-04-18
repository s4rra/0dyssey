from supabase import create_client, Client

# ⚙️ Replace these with your actual Supabase credentials
url = "your_supabase_url"
key = "your_supabase_key"
supabase: Client = create_client(url, key)

class RefUnit:
    def __init__(self, unitID=None, unitName="", unitDescription=None):
        self._unitID = unitID
        self._unitName = unitName
        self._unitDescription = unitDescription

    # 🧠 Getters & Setters
    def get_unitID(self): return self._unitID
    def set_unitID(self, val): self._unitID = val

    def get_unitName(self): return self._unitName
    def set_unitName(self, val): self._unitName = val

    def get_unitDescription(self): return self._unitDescription
    def set_unitDescription(self, val): self._unitDescription = val

    # 💾 Save to DB
    def persist_to_db(self):
        data = {
            "unitName": self._unitName,
            "unitDescription": self._unitDescription
        }
        res = supabase.table("RefUnit").insert(data).execute()
        return res

    # 🔍 Load from DB
    @staticmethod
    def from_db(unitID):
        res = supabase.table("RefUnit").select("*").eq("unitID", unitID).single().execute()
        if res.data:
            return RefUnit(
                unitID=res.data["unitID"],
                unitName=res.data["unitName"],
                unitDescription=res.data.get("unitDescription")
            )
        return None
