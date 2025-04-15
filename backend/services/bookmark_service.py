from config.settings import supabase_client

class BookmarkService:
    @staticmethod
    def add_bookmark(user_id, subunit_id):
        try:
            # Check if bookmark already exists
            existing = supabase_client.from_("Bookmarks").select("bookmarkID") \
                .eq("userID", user_id) \
                .eq("subUnitID", subunit_id) \
                .execute()
            
            if existing.data:
                return {"message": "Bookmark already exists"}, 200
            
            # Create new bookmark
            response = supabase_client.from_("Bookmarks").insert({
                "userID": user_id,
                "subUnitID": subunit_id
            }).execute()
            
            if not response.data:
                return {"error": "Failed to create bookmark"}, 500
                
            return {"message": "Bookmark added successfully"}, 201
        except Exception as e:
            print(f"Add bookmark error: {e}")
            return {"error": str(e)}, 500
    
    @staticmethod
    def remove_bookmark(user_id, subunit_id):
        try:
            response = supabase_client.from_("Bookmarks").delete() \
                .eq("userID", user_id) \
                .eq("subUnitID", subunit_id) \
                .execute()
            
            if not response.data:
                return {"error": "Bookmark not found"}, 404
                
            return {"message": "Bookmark removed successfully"}, 200
        except Exception as e:
            print(f"Remove bookmark error: {e}")
            return {"error": str(e)}, 500
    
    @staticmethod
    def get_user_bookmarks(user_id):
        try:
            # Fetch bookmarks with subunit details
            response = supabase_client.from_("Bookmarks") \
                .select("*, RefSubUnit!inner(subUnitID, subUnitName)") \
                .eq("userID", user_id) \
                .execute()
            
            # Transform the data for frontend consumption
            bookmarks = []
            for item in response.data:
                bookmark = {
                    "bookmarkID": item["bookmarkID"],
                    "subUnitID": item["RefSubUnit"]["subUnitID"],
                    "subUnitName": item["RefSubUnit"]["subUnitName"],
                    "createdAt": item.get("createdAt")
                }
                bookmarks.append(bookmark)
            
            return {"bookmarks": bookmarks}, 200
        except Exception as e:
            print(f"Get bookmarks error: {e}")
            return {"error": str(e)}, 500