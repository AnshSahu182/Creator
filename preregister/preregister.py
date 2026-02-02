from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

preregister_bp = Blueprint("preregister", __name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client['mydatabase']
preregister = db['mycollection']

@preregister_bp.route("/pre-register", methods=["POST"])
def pre_register():
    data = request.get_json()
    fullName = data.get("fullName")
    email = data.get("email")
    try:
        user_exists = preregister.find_one({'email': email})
        if user_exists:
            return jsonify({'error': 'User already exists'}), 400
        
        user = {
            'fullName': fullName,
            'email': email,
        }
        preregister.insert_one(user)
        return jsonify({
            "success": True,
            "message": f"Pre-registration successful for {fullName} ({email})"
    })
    except Exception as e:
        return jsonify({'error': str(e)}), 500