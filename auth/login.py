from datetime import timedelta
from flask import Blueprint,request,jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

bcrypt = Bcrypt()

client = MongoClient(os.getenv("MONGO_URI"))
db = client['creator_platform']
users = db['users']

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        user = users.find_one({'email': email})

        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check password
        if not bcrypt.check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401

        access_token = create_access_token(
            identity=str(user["_id"]),
            expires_delta=timedelta(minutes=15)
        )

        refresh_token = create_refresh_token(
            identity=str(user["_id"])
        )

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "plan": user.get("plan", "free")
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500