from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask import jsonify
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt

# from auth.extensions import oauth
from database.mongo import init_mongo,mongo
from auth.signup import google_signup,callback
from oauth_config import oauth
# Load env vars
load_dotenv()

# Flask app
app = Flask(__name__)
CORS(app)

# ---------------- CONFIG ----------------
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 86400  # 1 day

# OAuth config
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# oauth.init_app(app)
init_mongo(app)
bcrypt = Bcrypt(app)

# ---------------- INIT EXTENSIONS ----------------
jwt = JWTManager(app)
# oauth = OAuth(app)
oauth.init_app(app)

# ---------------- REGISTER GOOGLE OAUTH ----------------
# oauth.register(
#     name="google",
#     client_id=os.getenv("CLIENT_ID"),
#     client_secret=os.getenv("CLIENT_SECRET"),
#     access_token_url="https://oauth2.googleapis.com/token",
#     authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
#     api_base_url="https://www.googleapis.com/oauth2/v2/",
#     client_kwargs={
#         "scope": (
#             "openid email profile "
#             "https://www.googleapis.com/auth/youtube.readonly "
#             "https://www.googleapis.com/auth/yt-analytics.readonly"
#         ),
#         "access_type": "offline",
#         "prompt": "consent"
#     },
#     server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
# )

# ---------------- REGISTER BLUEPRINTS ----------------
# from auth.google_auth import google_auth_bp
from integrations.youtube import youtube_bp
from auth.login import login_bp
from auth.signup2 import signup_bp
from users.profile import profile_bp

# app.register_blueprint(google_auth_bp, url_prefix="/api/auth")
app.register_blueprint(youtube_bp, url_prefix="/api")
app.register_blueprint(login_bp, url_prefix="/api/auth")
app.register_blueprint(signup_bp, url_prefix="/api/auth")
app.register_blueprint(profile_bp, url_prefix="/api")
# ---------------- HEALTH CHECK ----------------
@app.route("/health", methods=["GET"])
def health_check():
    try:
        # simple MongoDB ping
        mongo.cx.admin.command("ping")

        return jsonify({
            "status": "ok",
            "app": "running",
            "database": "connected"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "app": "running",
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route("/api/auth/google", methods=["GET"])
def google_auth():
    return google_signup()

@app.route("/api/auth/callback", methods=["GET"])
def callback_route():
    return callback()

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True, port=3000)
