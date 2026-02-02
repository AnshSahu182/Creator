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

load_dotenv()

bcrypt=Bcrypt()

client=MongoClient(os.getenv('MongoClient_URI'))
db=client["creator"]
users=db["users"]

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
    redirect_uri=url_for('callback_route',_external=True)
    return google.authorize_redirect(redirect_uri)

#Login using google
# @app.route('/googlelogin', methods=['POST'])
#data here does not goto server it goes to google and it send redirected url that is why there is GET 
def google_login():
    redirect_uri=url_for('callback_route',_external=True)
    return google.authorize_redirect(redirect_uri)

#Callback (Direct google login ka data deta h )
#@app.route("/callback", methods=['GET'])
#data here does not go to server it goes to google and it send redirected url that is why there is GET 
def callback():
    token=google.authorize_access_token()  # exchange code for token
    user_info=google.get('userinfo').json() #get user data from token

    email=user_info.get('email')
    name=user_info.get('name')
    picture=user_info.get("picture")

    user=users.find_one({'email':email})
    if  user:
        users.update_one(
            {'email':email},{"$set":{"image":picture,"updatedAt":datetime.utcnow()}})
        
    else:
        users.insert_one({
            "username":name,
            "email":email,
            "password":None,
            "image":picture,
            "createdAt":datetime.utcnow(),
            "updatedAt":datetime.utcnow(),
            "refreshToken":None
        })
    access_token=create_access_token(identity=email)
    refresh_token=create_refresh_token(identity=email)
    users.update_one(
        {"email":email},
        {"$set":{"refreshToken":refresh_token}}
    )

    # Detect if frontend requested a redirect
    is_browser = "text/html" in request.headers.get("Accept", "")

    if is_browser:
        # REDIRECT path for browser login
        frontend_url = "https://tech-bay-pi.vercel.app/"
        return redirect(f"{frontend_url}?access_token={access_token}")

    return jsonify({
        "message": "Login successful",
        "email": email,
        "access_token": access_token,
        "refresh_token": refresh_token
    })
