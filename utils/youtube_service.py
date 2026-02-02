import os
import requests
from cryptography.fernet import Fernet

from database.mongo import mongo

# Crypto
fernet = Fernet(os.getenv("FERNET_KEY"))

def decrypt_token(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()


def get_youtube_access_token(email: str) -> str:
    record =  mongo.db.social_accounts.find_one({
        "email": email,
        "provider": "youtube"
    })

    if not record:
        raise Exception("YouTube account not connected")

    refresh_token = decrypt_token(record["refreshToken"])

    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
    ).json()

    return response.get("access_token")
