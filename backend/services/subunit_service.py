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
    
    @staticmethod
    def add_bookmark(user_id, subunit_id):
        try:
            # Check if subunit exists
            subunit_response = (
                supabase_client.from_("RefSubUnit")
                .select("subUnitID")
                .eq("subUnitID", subunit_id)
                .execute()
            )
            if not subunit_response.data:
                return {"error": "Subunit not found"}, 404
            
            # Check if bookmark already exists
            existing_bookmark = (
                supabase_client.from_("Bookmarks")
                .select("*")
                .eq("userID", user_id)
                .eq("subUnitID", subunit_id)
                .execute()
            )
            if existing_bookmark.data:
                return {"error": "Bookmark already exists"}, 400
            
            # Add new bookmark
            new_bookmark = {
                "userID": user_id,
                "subUnitID": subunit_id
            }
            response = supabase_client.from_("Bookmarks").insert(new_bookmark).execute()
            
            if response.data:
                return {"message": "Bookmark added successfully"}, 201
            else:
                return {"error": "Failed to add bookmark"}, 500
        
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def remove_bookmark(user_id, subunit_id):
        try:
            response = (
                supabase_client.from_("Bookmarks")
                .delete()
                .eq("userID", user_id)
                .eq("subUnitID", subunit_id)
                .execute()
            )
            
            if len(response.data) > 0:
                return {"message": "Bookmark removed successfully"}, 200
            else:
                return {"error": "Bookmark not found"}, 404
        
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_user_bookmarks(user_id):
        try:
            response = (
                supabase_client.from_("Bookmarks")
                .select("subUnitID, RefSubUnit(subUnitName, subUnitContent)")
                .eq("userID", user_id)
                .execute()
            )
            
            bookmarks = []
            for bookmark in response.data:
                subunit = bookmark.get('RefSubUnit', {})
                # Parse JSON content if it's a string
                if isinstance(subunit.get('subUnitContent'), str):
                    try:
                        subunit['subUnitContent'] = json.loads(subunit['subUnitContent'])
                    except json.JSONDecodeError:
                        pass
                bookmarks.append({
                    "subUnitID": bookmark['subUnitID'],
                    "subUnitName": subunit.get('subUnitName'),
                    "subUnitContent": subunit.get('subUnitContent')
                })
            
            return {"bookmarks": bookmarks}, 200
        
        except Exception as e:
            return {"error": str(e)}, 500
