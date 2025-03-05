from flask import Flask, jsonify
import supabase
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase_client = create_client(url, key)

@app.route('/user-data', methods=['GET'])
def fetch_user_data():
    try:
        user_id = 4 #user_id should be a paremeter, but its hardcoded for testing now
        response = (
        supabase_client.table("User")
         .select("RefSkillLevel(skillLevel)","RefUnit(unitDescription)","RefSubUnit(subUnitDescription)")
         .eq("userID", user_id)
         .execute()
        )
        return jsonify(response.data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)