from flask import Flask, jsonify, request
from flask_cors import CORS
import supabase
from supabase import create_client

app = Flask(__name__)
CORS(app)  

SUPABASE_URL = "http://sarra.tailefeb94.ts.net:8000/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/courses', methods=['GET'])
def get_courses():
    try:
        response = supabase_client.table("RefUnit").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/courses', methods=['POST'])
def add_course():
    try:
        data = request.get_json()
        new_course = {
            "unitID": data.get("unitID"),
            "unitName": data.get("unitName"),
        }
        response = supabase_client.table("RefUnit").insert(new_course).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
