import json
from config.settings import supabase_client

class SubunitService:
    @staticmethod
    def get_subunit_content(subunit_id):
        try:
            response = (
                supabase_client.from_("RefSubUnit")
                .select("subUnitID, subUnitName, subUnitContent")
                .eq("subUnitID", subunit_id)
                .execute()
            )
            
            if not response.data:
                return {"error": "Subunit not found"}, 404
            
            subunit = response.data[0]
            
            # If content is a JSON string, try parsing it
            if isinstance(subunit.get('subUnitContent'), str):
                try:
                    subunit['subUnitContent'] = json.loads(subunit['subUnitContent'])
                except json.JSONDecodeError:
                    pass

            return subunit, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def add_subunit(data): 
        try:
            new_subunit = {
                "subUnitName": data.get("subUnitName"),
                "subUnitContent": json.dumps(data.get("subUnitContent", "")),
            }
            response = supabase_client.from_("RefSubUnit").insert(new_subunit).execute()
            
            if response.data:
                return response.data, 201
            else:
                return {"error": "Failed to add subunit"}, 500
        
        except Exception as e:
            return {"error": str(e)}, 500
    
   