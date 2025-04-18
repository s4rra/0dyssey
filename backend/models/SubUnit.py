from supabase import create_client, Client

# ⚙️ Supabase setup (swap these with your real credentials)
url = "your_supabase_url"
key = "your_supabase_key"
supabase: Client = create_client(url, key)

class RefSubUnit:
    def __init__(self, subUnitID=None, subUnitName="", unitID=None, 
                 subUnitDescription=None, subUnitContent=None):
        self._subUnitID = subUnitID
        self._subUnitName = subUnitName
        self._unitID = unitID
        self._subUnitDescription = subUnitDescription
        self._subUnitContent = subUnitContent  # should be a dict (jsonb)

    # 🧠 Getters & Setters
    def get_subUnitID(self): return self._subUnitID
    def set_subUnitID(self, val): self._subUnitID = val

    def get_subUnitName(self): return self._subUnitName
    def set_subUnitName(self, val): self._subUnitName = val

    def get_unitID(self): return self._unitID
    def set_unitID(self, val): self._unitID = val

    def get_subUnitDescription(self): return self._subUnitDescription
    def set_subUnitDescription(self, val): self._subUnitDescription = val

    def get_subUnitContent(self): return self._subUnitContent
    def set_subUnitContent(self, val): self._subUnitContent = val

    # 💾 Save to DB
    def persist_to_db(self):
        data = {
            "subUnitName": self._subUnitName,
            "unitID": self._unitID,
            "subUnitDescription": self._subUnitDescription,
            "subUnitContent": self._subUnitContent
        }
        res = supabase.table("RefSubUnit").insert(data).execute()
        return res

    # 🔍 Fetch from DB
    @staticmethod
    def from_db(subUnitID):
        res = supabase.table("RefSubUnit").select("*").eq("subUnitID", subUnitID).single().execute()
        if res.data:
            return RefSubUnit(
                subUnitID=res.data["subUnitID"],
                subUnitName=res.data["subUnitName"],
                unitID=res.data.get("unitID"),
                subUnitDescription=res.data.get("subUnitDescription"),
                subUnitContent=res.data.get("subUnitContent")
            )
        return None
