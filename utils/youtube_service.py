import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
from utils.encryption import decrypt_token

client=MongoClient(os.getenv('MONGO_URI'))
db=client["creator_platform"]
social_accounts=db["social_accounts"]


def get_youtube_access_token(email: str) -> str:
    record =  social_accounts.find_one({
        "email": email,
        "provider": "youtube"
    })

    if not record:
        raise Exception("YouTube account not connected")

    refresh_token = decrypt_token(record["refreshToken"])
    # refresh_token = record["refreshToken"]

    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
    )
    data = response.json()
    print("YouTube token refresh response:", data)

    return response.get("access_token")


# import os
# from datetime import datetime
# from pymongo import MongoClient
# from oauth_config import oauth
# from utils.encryption import encrypt_token

# # ---------------- DB ----------------
# client = MongoClient(os.getenv("MONGO_URI"))
# db = client["creator_platform"]
# social_accounts = db["social_accounts"]

# # ---------------- SERVICE ----------------
# def handle_youtube_callback():
#     token = oauth.google.authorize_access_token()
#     print("GOOGLE TOKEN RESPONSE:", token)

#     refresh_token = token.get("refresh_token")

#     if not refresh_token:
#         raise Exception(
#             "Google did not return a refresh token. "
#             "User must re-consent."
#         )

#     user_info = oauth.google.get("userinfo").json()
#     email = user_info["email"]

#     # 🔐 Store refresh token securely
#     social_accounts.update_one(
#         {"email": email, "provider": "youtube"},
#         {
#             "$set": {
#                 "refreshToken": encrypt_token(refresh_token),
#                 "updatedAt": datetime.utcnow()
#             },
#             "$setOnInsert": {
#                 "connectedAt": datetime.utcnow()
#             }
#         },
#         upsert=True
#     )

#     return {
#         "success": True,
#         "message": "YouTube connected successfully"
#     }
