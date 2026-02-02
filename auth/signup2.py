# from flask import Blueprint,request,jsonify
# from flask_jwt_extended import create_access_token, create_refresh_token
# from datetime import timedelta
# import bcrypt

# from database.mongo import mongo

# signup_bp = Blueprint('signup', __name__)

# @signup_bp.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     fullName = data.get('fullName')
#     email = data.get('email')
#     password = data.get('password')
#     try:
#         user_exists = mongo.db.users.find_one({'email': email})
#         if user_exists:
#             return jsonify({'error': 'User already exists'}), 400
        
#         hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#         user = {
#             'fullName': fullName,
#             'email': email,
#             'plan' : 'free',
#             'password': hashed_password,    
#             "refresh_token": refresh_token
#         }

#         access_token = create_access_token(
#         identity=str(user["_id"]),
#         expires_delta=timedelta(minutes=15)
#         )

#         refresh_token = create_refresh_token(
#             identity=str(user["_id"])
#         )

#         mongo.db.users.insert_one(user)
#         return jsonify({
#             "access_token": access_token,
#             "refresh_token": refresh_token,
#             "user": {
#                 "id": str(user["_id"]),
#                 "email": user["email"],
#                 "plan": user.get("plan", "free")
#             }
#         })
    
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from database.mongo import mongo
from flask_bcrypt import Bcrypt   # if using flask-bcrypt
from datetime import datetime

bcrypt = Bcrypt()

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        fullName = data.get('fullName')
        email = data.get('email')
        password = data.get('password')

        # check existing user
        if mongo.db.users.find_one({"email": email}):
            return jsonify({"error": "User already exists"}), 400

        # hash password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # insert user FIRST
        result = mongo.db.users.insert_one({
            "fullName": fullName,
            "email": email,
            "password": hashed_password,
            "plan": "free",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        })

        user_id = str(result.inserted_id)

        # now create tokens
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(minutes=15)
        )

        refresh_token = create_refresh_token(identity=user_id)

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
