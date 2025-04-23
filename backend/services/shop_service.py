from config.settings import supabase_client
from datetime import datetime, timezone
import uuid

class ShopService:
    @staticmethod
    def get_shop_items(user_id):
        """Get all items in the shop and mark which ones the user owns"""
        try:
            shop_items = supabase_client.from_("Shop").select("*").execute()
 
            user_purchases = supabase_client.from_("UserPurchases") \
                .select("itemID") \
                .eq("userID", user_id) \
                .execute()

            purchased_ids = {item["itemID"] for item in user_purchases.data}
            
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
            # Check if user already owns this item (for non-consumable items)
            existing_purchase = supabase_client.from_("UserPurchases") \
                .select("purchaseID") \
                .eq("userID", user_id) \
                .eq("itemID", item_id) \
                .execute()
                
            # Get the item details
            item = supabase_client.from_("Shop") \
                .select("*") \
                .eq("itemID", item_id) \
                .execute()
                
            if not item.data:
                return {"error": "Item not found"}, 404
                
            item_data = item.data[0]
            item_cost = item_data["pointCost"]
            item_type = item_data.get("itemType")
            
            # Get user's current points
            user = supabase_client.from_("User") \
                .select("points, hints") \
                .eq("userID", user_id) \
                .execute()
                
            if not user.data:
                return {"error": "User not found"}, 404
                
            user_data = user.data[0]
            user_points = user_data["points"]
            current_hints = user_data.get("hints", 0)

            # Check if user has enough points
            if user_points < item_cost:
                return {"error": "Not enough points"}, 400
            
            # For non-consumable items (like profile pictures), check if already owned
            if item_type != "hint" and existing_purchase.data:
                return {"error": "You already own this item"}, 400
                
            # Deduct points from user
            update_data = {"points": user_points - item_cost}
            
            # If it's a hint purchase, increment the hint count
            if item_type == "hint":
                # Get the hint quantity from the item
                hint_quantity = item_data.get("quantity", 1)
                update_data["hints"] = current_hints + hint_quantity
            
            # Update the user's points and hints if applicable
            update_user = supabase_client.from_("User") \
                .update(update_data) \
                .eq("userID", user_id) \
                .execute()
                
            if not update_user.data:
                return {"error": "Failed to update user data"}, 500

            # Record the purchase in UserPurchases table
            current_time = datetime.now(timezone.utc).isoformat()
            
            if item_type == "hint":
                # For hints, add them to the user's hint inventory
                # First, check if HintInventory table exists, if not create it
                try:
                    # Add hint to user's inventory
                    hint_quantity = item_data.get("quantity", 1)
                    
                    # Record each hint purchase individually to track usage
                    for _ in range(hint_quantity):
                        inventory_id = str(uuid.uuid4())
                        hint_inventory = supabase_client.from_("HintInventory").insert({
                            "inventoryID": inventory_id,
                            "userID": user_id,
                            "itemID": item_id,
                            "purchaseDate": current_time,
                            "used": False
                        }).execute()
                        
                        if not hint_inventory.data:
                            # Log the error but continue
                            print(f"Failed to add hint to inventory: {hint_inventory.error}")
                    
                    # Also record the transaction in UserPurchases for history
                    purchase = supabase_client.from_("UserPurchases").insert({
                        "userID": user_id,
                        "itemID": item_id,
                        "purchaseDate": current_time,
                        "quantity": hint_quantity
                    }).execute()
                    
                except Exception as hint_error:
                    print(f"Error adding hints to inventory: {hint_error}")
                    # Continue execution even if hint inventory fails
            else:
                # For non-hint items like profile pictures
                purchase = supabase_client.from_("UserPurchases").insert({
                    "userID": user_id,
                    "itemID": item_id,
                    "purchaseDate": current_time
                }).execute()
                
                if not purchase.data:
                    # Rollback the points deduction
                    supabase_client.from_("User").update({"points": user_points}).eq("userID", user_id).execute()
                    return {"error": "Failed to record purchase"}, 500
                    
            return {
                "message": "Purchase successful", 
                "item": item_data,
                "remainingPoints": user_points - item_cost,
                "currentHints": update_data.get("hints", current_hints)
            }, 200
                
        except Exception as e:
            print(f"Error purchasing item: {e}")
            return {"error": str(e)}, 500
    
    @staticmethod
    def get_user_purchases(user_id):
        """Get all items purchased by the user"""
        try:
            purchases = supabase_client.from_("UserPurchases") \
                .select("*, Shop(*)") \
                .eq("userID", user_id) \
                .execute()
                
            return purchases.data, 200
            
        except Exception as e:
            print(f"Error getting user purchases: {e}")
            return {"error": str(e)}, 500
            
    @staticmethod
    def get_user_hint_inventory(user_id):
        """Get all available hints in the user's inventory"""
        try:
            hints = supabase_client.from_("HintInventory") \
                .select("*, Shop(*)") \
                .eq("userID", user_id) \
                .eq("used", False) \
                .execute()
                
            return hints.data, 200
            
        except Exception as e:
            print(f"Error getting user hint inventory: {e}")
            return {"error": str(e)}, 500
    
    @staticmethod
    def use_hint(user_id, inventory_id):
        """Mark a hint as used in the user's inventory"""
        try:
            # Verify the hint belongs to the user
            hint = supabase_client.from_("HintInventory") \
                .select("inventoryID") \
                .eq("inventoryID", inventory_id) \
                .eq("userID", user_id) \
                .eq("used", False) \
                .execute()
                
            if not hint.data:
                return {"error": "Hint not found or already used"}, 404
                
            # Mark the hint as used
            update_hint = supabase_client.from_("HintInventory") \
                .update({"used": True, "useDate": datetime.now(timezone.utc).isoformat()}) \
                .eq("inventoryID", inventory_id) \
                .execute()
                
            if not update_hint.data:
                return {"error": "Failed to use hint"}, 500
                
            # Also update the User.hints count to decrement by 1
            user = supabase_client.from_("User") \
                .select("hints") \
                .eq("userID", user_id) \
                .execute()
                
            if user.data and "hints" in user.data[0]:
                current_hints = user.data[0]["hints"]
                if current_hints > 0:
                    supabase_client.from_("User") \
                        .update({"hints": current_hints - 1}) \
                        .eq("userID", user_id) \
                        .execute()
                
            return {"message": "Hint used successfully"}, 200
            
        except Exception as e:
            print(f"Error using hint: {e}")
            return {"error": str(e)}, 500