from urllib import response
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
from utils.youtube_service import get_youtube_access_token

youtube_bp = Blueprint("youtube", __name__)


@youtube_bp.route("/youtube", methods=["GET"])
@jwt_required()
def youtube_dashboard():
    try:
        email = get_jwt_identity()
        access_token = get_youtube_access_token(email)
        # print("YouTube Access Token: #################################")

        response = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "part": "snippet,statistics,brandingSettings,contentDetails",
                "mine": True
            }
        )
        # print("YouTube API status:", response.status_code)
        # print("YouTube API response:", response.text)

        data = response.json()
        channel = data["items"][0]

        dashboard_data = {
            "channelId": channel["id"],
            "channelName": channel["snippet"]["title"],
            "description": channel["snippet"]["description"],
            "customUrl": channel["snippet"].get("customUrl"),
            "profileImage": channel["snippet"]["thumbnails"]["high"]["url"],
            "subscribers": channel["statistics"].get("subscriberCount"),
            "totalViews": channel["statistics"].get("viewCount"),
            "totalVideos": channel["statistics"].get("videoCount"),
            "madeForKids": channel["brandingSettings"]["channel"].get("madeForKids"),
            "uploadsPlaylistId": channel["contentDetails"]["relatedPlaylists"]["uploads"]
        }

        return jsonify({"connected": True, "youtube": dashboard_data}), 200

    except Exception as e:
        return jsonify({"connected": False, "error": str(e)}), 400

# from flask import Blueprint, jsonify, url_for
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from oauth_config import oauth

# youtube_bp = Blueprint("youtube", __name__)

# # 🔗 Step 1: Redirect user to Google for YouTube consent
# @youtube_bp.route("/youtube/connect", methods=["GET"])
# @jwt_required()
# def connect_youtube():
#     email = get_jwt_identity()

#     redirect_uri = url_for("youtube.youtube_callback", _external=True)

#     return oauth.google.authorize_redirect(
#         redirect_uri,
#         access_type="offline",
#         prompt="consent",
#         login_hint=email
#     )


# # 🔁 Step 2: Google callback
# @youtube_bp.route("/youtube/callback", methods=["GET"])
# def youtube_callback():
#     from utils.youtube_service import handle_youtube_callback

#     try:
#         result = handle_youtube_callback()
#         return jsonify(result), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400
