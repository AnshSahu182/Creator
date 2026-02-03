from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client['creator_platform']
users = db['users']

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    try:
        # get user id from JWT
        user_id = get_jwt_identity()

        # # find user in database
        # user = mongo.db.users.find_one(
        #     {"_id": mongo.db.users.database.client.get_database().codec_options.document_class(user_id)}
        # )

        # ❌ above is too complex, so instead do this 👇
        from bson import ObjectId
        user = users.find_one({"_id": ObjectId(user_id)})

        if not user:
            return jsonify({"error": "User not found"}), 404

        # return user details (NO PASSWORD)
        return jsonify({
            "id": str(user["_id"]),
            "fullName": user.get("fullName"),
            "email": user.get("email"),
            "plan": user.get("plan", "free"),
            "createdAt": user.get("createdAt").isoformat() if user.get("createdAt") else None,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
