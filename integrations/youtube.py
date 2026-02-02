# from flask import Blueprint, redirect, request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity
# import requests
# from database.mongo import mongo
# from utils.youtube_service import get_youtube_access_token

# youtube_bp = Blueprint('youtube', __name__)

# @youtube_bp.route("/api/youtube/dashboard", methods=["GET"])
# @jwt_required()
# def youtube_dashboard():
#     try:
#         email = get_jwt_identity()

#         access_token = get_youtube_access_token(email)

#         response = requests.get(
#             "https://www.googleapis.com/youtube/v3/channels",
#             headers={
#                 "Authorization": f"Bearer {access_token}"
#             },
#             params={
#                 "part" : "snippet,statistics,brandingSettings,contentDetails",
#                 "mine": True
#             }
#         )

#         data = response.json()

#         if not data.get("items"):
#             return jsonify({"error": "No YouTube channel found"}), 404

#         channel = data["items"][0]

#         dashboard_data = {
#             "channelId": channel["id"],
#             "channelName": channel["snippet"]["title"],
#             "description": channel["snippet"]["description"],
#             "customUrl": channel["snippet"].get("customUrl"),
#             "profileImage": channel["snippet"]["thumbnails"]["high"]["url"],
#             "subscribers": channel["statistics"].get("subscriberCount"),
#             "totalViews": channel["statistics"].get("viewCount"),
#             "totalVideos": channel["statistics"].get("videoCount"),
#             "madeForKids": channel["brandingSettings"]["channel"].get("madeForKids"),
#             "uploadsPlaylistId": channel["contentDetails"]["relatedPlaylists"]["uploads"]
# }

#         return jsonify({
#             "connected": True,
#             "youtube": dashboard_data
#         }), 200

#     except Exception as e:
#         return jsonify({
#             "connected": False,
#             "error": str(e)
#         }), 400

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

        response = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "part": "snippet,statistics,brandingSettings,contentDetails",
                "mine": True
            }
        )

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
