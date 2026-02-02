from flask import request,jsonify, url_for
#from authlib.integrations.flask_client import OAuth # for login
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime
from flask import redirect
from oauth_config import oauth
from utils.encryption import encrypt_token

load_dotenv()

bcrypt=Bcrypt()

client=MongoClient(os.getenv('MongoClient_URI'))
db=client["creator_platfrom"]
users=db["users"]
social_accounts=db["social_accounts"]

# 🔑 Google OAuth Configuration
google = oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


# Sign up using google
# @app.route('/googlesignup', methods=['GET'])
def google_signup():
    return oauth.google.authorize_redirect(
        "https://creator-t9nt.onrender.com/api/auth/callback"
    )

#Callback (Direct google login ka data deta h )
#@app.route("/callback", methods=['GET'])
#data here does not go to server it goes to google and it send redirected url that is why there is GET 
def callback():
    token = oauth.google.authorize_access_token()

    google_refresh_token = token.get("refresh_token")

    user_info = oauth.google.get("userinfo").json()
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    if google_refresh_token:
        social_accounts.update_one(
            {"email": email, "provider": "youtube"},
            {
                "$set": {
                    "refreshToken": encrypt_token(google_refresh_token),
                    "connectedAt": datetime.utcnow()
                }
            },
            upsert=True
        )

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    users.update_one(
        {"email": email},
        {
            "$set": {
                "fullName": name,
                "image": picture,
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
        "refresh_token": refresh_token
    })
    # return redirect(
    #     f"https://imprecatory-grady-biophysically.ngrok-free.dev/dashboard?access_token={access_token}"
    # )
