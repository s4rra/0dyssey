# shop_service.py
from config.settings import supabase_client
from datetime import datetime, timezone

class ShopService:
    @staticmethod
    def get_shop_items(user_id):
        """Get all items in the shop and mark which ones the user owns"""
        try:
            # Get all shop items
            shop_items = supabase_client.from_("Shop").select("*").execute()
            
            # Get user's purchased items
            user_purchases = supabase_client.from_("UserPurchases") \
                .select("itemID") \
                .eq("userID", user_id) \
                .execute()
            
            # Create a set of purchased item IDs for quick lookup
            purchased_ids = {item["itemID"] for item in user_purchases.data}
            
            # Mark items as purchased or not
            for item in shop_items.data:
                item["purchased"] = item["itemID"] in purchased_ids
            
            return shop_items.data, 200
            
        except Exception as e:
            print(f"Error getting shop items: {e}")
            return {"error": str(e)}, 500
    
    @staticmethod
    def purchase_item(user_id, item_id):
        """Purchase an item from the shop"""
        try:
            # Check if user already owns this item
            existing_purchase = supabase_client.from_("UserPurchases") \
                .select("purchaseID") \
                .eq("userID", user_id) \
                .eq("itemID", item_id) \
                .execute()
                
            if existing_purchase.data:
                return {"error": "You already own this item"}, 400
            
            # Get item price
            item = supabase_client.from_("Shop") \
                .select("*") \
                .eq("itemID", item_id) \
                .execute()
                
            if not item.data:
                return {"error": "Item not found"}, 404
                
            item_cost = item.data[0]["pointCost"]
            
            # Get user's current points
            user = supabase_client.from_("User") \
                .select("points") \
                .eq("userID", user_id) \
                .execute()
                
            if not user.data:
                return {"error": "User not found"}, 404
                
            user_points = user.data[0]["points"]
            
            # Check if user has enough points
            if user_points < item_cost:
                return {"error": "Not enough points"}, 400
                
            # Start a transaction
            # Note: Supabase JS client doesn't have direct transaction support
            # so we'll do our best with separate operations
            
            # Deduct points from user
            update_points = supabase_client.from_("User") \
                .update({"points": user_points - item_cost}) \
                .eq("userID", user_id) \
                .execute()
                
            if not update_points.data:
                return {"error": "Failed to update points"}, 500
                
            # Add purchase record
            purchase = supabase_client.from_("UserPurchases") \
                .insert({
                    "userID": user_id,
                    "itemID": item_id,
                    "purchaseDate": datetime.now(timezone.utc).isoformat()
                }) \
                .execute()
                
            if not purchase.data:
                # Try to rollback points deduction
                supabase_client.from_("User") \
                    .update({"points": user_points}) \
                    .eq("userID", user_id) \
                    .execute()
                return {"error": "Failed to record purchase"}, 500
                
            return {
                "message": "Purchase successful", 
                "item": item.data[0],
                "remainingPoints": user_points - item_cost
            }, 200
            
        except Exception as e:
            print(f"Error purchasing item: {e}")
            return {"error": str(e)}, 500
    
    @staticmethod
    def get_user_purchases(user_id):
        """Get all items purchased by the user"""
        try:
            # Join UserPurchases with Shop to get item details
            purchases = supabase_client.from_("UserPurchases") \
                .select("*, Shop(*)") \
                .eq("userID", user_id) \
                .execute()
                
            return purchases.data, 200
            
        except Exception as e:
            print(f"Error getting user purchases: {e}")
            return {"error": str(e)}, 500