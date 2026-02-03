from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from flask_bcrypt import Bcrypt   # if using flask-bcrypt
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

bcrypt = Bcrypt()

client = MongoClient(os.getenv("MONGO_URI"))
db = client['creator_platform']
users = db['users']

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        fullName = data.get('fullName')
        email = data.get('email')
        password = data.get('password')

        # check existing user
        if users.find_one({"email": email}):
            return jsonify({"error": "User already exists"}), 400

        # hash password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        refresh_token = create_refresh_token(identity=email)

        # insert user FIRST
        result = users.insert_one({
            "fullName": fullName,
            "email": email,
            "password": hashed_password,
            "plan": "free",
            "refresh_token": refresh_token,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        })

        user_id = str(result.inserted_id)

        # now create tokens
        access_token = create_access_token(
            identity=email,
            expires_delta=timedelta(minutes=15)
        )

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user_id,
                "email": email,
                "plan": "free",
            }
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
