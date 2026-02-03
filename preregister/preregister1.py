from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import os
load_dotenv()
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URI"))
db = client['creator_platform']
preregister_users = db['preregister']

preregister_bp = Blueprint("preregister", __name__)

@preregister_bp.route("/preregister", methods=["POST"])
def preregister_user():
    try:
        data = request.get_json(force=True)

        full_name = data.get("fullName")
        email = data.get("email")

        if not full_name or not email:
            return jsonify({
                "error": "fullName and email are required"
            }), 400
        

        # check if user already exists
        if preregister_users.find_one({"email": email}):
            return jsonify({
                "error": "User already exists"
            }), 400

        preregister_users.insert_one({
            "fullName": full_name,
            "email": email
        })

        return jsonify({
            "success": True,
            "message": f"Pre-registration successful for {full_name} ({email})"
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
