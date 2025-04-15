from flask import Blueprint, request, jsonify
from services.performance_service import PerformanceService
from utils.auth import verify_token

performance_bp = Blueprint("performance_bp", __name__)

@performance_bp.route("/performance/submit/<int:unit_id>/<int:subunit_id>", methods=["POST"])
def submit_performance(unit_id, subunit_id):
    try:
        auth_result = verify_token()
        if isinstance(auth_result, tuple):
            return jsonify(auth_result[0]), auth_result[1]
        
        user_id = auth_result["id"]
        
        answers_data = request.get_json()
        if not answers_data or not isinstance(answers_data, list):
            return jsonify({"error": "Invalid request data. Expected list of answers."}), 400
            
        service = PerformanceService(user_id)
        result = service.update_performance(unit_id, subunit_id, answers_data)
        
        if not result.get("success"):
            return jsonify({"error": result.get("error", "Failed to update performance")}), 500
            
        return jsonify({"message": "Performance updated successfully", 
                        "performanceID": result.get("performanceID")}), 200
                        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@performance_bp.route("/performance/unit/<int:unit_id>", methods=["POST"])
def analyze_unit_performance(unit_id):
    try:
        auth_result = verify_token()
        if isinstance(auth_result, tuple):
            return jsonify(auth_result[0]), auth_result[1]
            
        user_id = auth_result["id"]
        
        service = PerformanceService(user_id)
        result = service.model_feedback(unit_id)
        
        if not result.get("success"):
            return jsonify({"error": result.get("error", "Failed to generate AI feedback")}), 500
            
        return jsonify({
            "message": "AI feedback generated successfully", 
            "feedback": result.get("feedback")
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@performance_bp.route("/performance/dashboard", methods=["GET"])
def get_dashboard_summary():
    try:
        auth_result = verify_token()
        if isinstance(auth_result, tuple):
            return jsonify(auth_result[0]), auth_result[1]
            
        user_id = auth_result["id"]
        
        service = PerformanceService(user_id)
        dashboard_data = service.get_summary()
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@performance_bp.route("/performance/subunit/<int:subunit_id>", methods=["GET"])
def get_subunit_performance(subunit_id):
    try:
        auth_result = verify_token()
        if isinstance(auth_result, tuple):
            return jsonify(auth_result[0]), auth_result[1]
            
        user_id = auth_result["id"]
        
        service = PerformanceService(user_id)
        performance = service.get_performance(subunit_id)
        
        if not performance:
            return jsonify({"message": "No performance data found for this subunit"}), 404
            
        return jsonify(performance), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500