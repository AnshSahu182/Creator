from flask import request,jsonify
#from authlib.integrations.flask_client import OAuth # for login
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime
from oauth_config import oauth
from utils.encryption import encrypt_token
import json
load_dotenv()

bcrypt=Bcrypt()

client = MongoClient(os.getenv("MONGO_URI"))
db = client['creator_platform']
users = db['users']
social_accounts = db['social_accounts']

# 🔑 Google OAuth Configuration
google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        "scope": (
            "openid email profile "
            "https://www.googleapis.com/auth/youtube.readonly"
        ),
        "access_type": "offline",   # 🔑 REQUIRED
        "prompt": "consent"         # 🔑 REQUIRED
    }
)


# Sign up using google
# @app.route('/googlesignup', methods=['GET'])
def google_signup():
    return oauth.google.authorize_redirect(os.getenv('CALLBACK_URL'))

# ---------------- CALLBACK ----------------
def callback():
    token = oauth.google.authorize_access_token()
    # print( json.dumps(token, indent=2) )

    new_refresh_token = token.get("refresh_token")
    # print ("Google OAuth token:", new_refresh_token)

    user_info = oauth.google.get("userinfo").json()
    email = user_info["email"]
    name = user_info.get("name")
    picture = user_info.get("picture")

    # 🔐 HANDLE REFRESH TOKEN CORRECTLY
    existing = social_accounts.find_one({
        "email": email,
        "provider": "youtube"
    })

    if new_refresh_token:
        # ✅ Google gave a new refresh token
        encrypted = encrypt_token(new_refresh_token)

        social_accounts.update_one(
            {"email": email, "provider": "youtube"},
            {
                "$set": {
                    "refreshToken": encrypted,
                    "updatedAt": datetime.utcnow()
                },
                "$setOnInsert": {
                    "connectedAt": datetime.utcnow()
                }
            },
            upsert=True
        )

    elif existing:
        # ✅ Reuse old refresh token
        encrypted = existing["refreshToken"]

    else:
        encrypted = None  # user never granted YouTube access

    # ---------------- JWT ----------------
    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    users.update_one(
        {"email": email},
        {
            "$set": {
                "fullName": name,
                "image": picture,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "updatedAt": datetime.utcnow()
            },
            "$setOnInsert": {
                "createdAt": datetime.utcnow()
            }
        },
        upsert=True
    )

    return jsonify({
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "google_refresh_token_available": encrypted is not None
    })
