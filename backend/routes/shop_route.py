# shop_route.py
from flask import Blueprint, request, jsonify
from services.shop_service import ShopService
from utils.auth import verify_token

shop_bp = Blueprint("shop_bp", __name__)

@shop_bp.route("/shop/items", methods=["GET"])
def get_shop_items():
    """Get all items available in the shop"""
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = ShopService.get_shop_items(user["id"])
    return jsonify(result), status_code

@shop_bp.route("/shop/purchase", methods=["POST"])
def purchase_item():
    """Purchase an item from the shop"""
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    data = request.json
    result, status_code = ShopService.purchase_item(user["id"], data.get("itemID"))
    return jsonify(result), status_code

@shop_bp.route("/shop/user-purchases", methods=["GET"])
def get_user_purchases():
    """Get all items purchased by the user"""
    auth_result = verify_token()
    if isinstance(auth_result, tuple):
        return jsonify(auth_result[0]), auth_result[1]
    
    user = auth_result
    result, status_code = ShopService.get_user_purchases(user["id"])
    return jsonify(result), status_code