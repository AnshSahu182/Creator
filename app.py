from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask import jsonify
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt
from pymongo import MongoClient

# from auth.extensions import oauth
from auth.google_auth import google_signup,callback
from oauth_config import oauth


# Flask app
app = Flask(__name__)
CORS(app)

# ---------------- CONFIG ----------------
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 86400  # 1 day

# OAuth config
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

client = MongoClient(os.getenv("MONGO_URI"))

bcrypt = Bcrypt(app)

# ---------------- INIT EXTENSIONS ----------------
jwt = JWTManager(app)

oauth.init_app(app)

# ---------------- REGISTER BLUEPRINTS ----------------
# from auth.google_auth import google_auth_bp
from integrations.youtube import youtube_bp
from auth.login import login_bp
from auth.signup import signup_bp
from users.profile import profile_bp
from preregister.preregister1 import preregister_bp

# app.register_blueprint(google_auth_bp, url_prefix="/api/auth")
app.register_blueprint(youtube_bp, url_prefix="/api")
app.register_blueprint(login_bp, url_prefix="/api/auth")
app.register_blueprint(signup_bp, url_prefix="/api/auth")
app.register_blueprint(profile_bp, url_prefix="/api")
app.register_blueprint(preregister_bp, url_prefix="/api")
# ---------------- HEALTH CHECK ----------------
@app.route("/", methods=["GET"])
def health_check():
    try:
        return jsonify({
            "status": "ok",
            "app": "running",
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "app": "running",
            "error": str(e)
        }), 500

@app.route("/db_health", methods=["GET"])
def db_health_check():
    try:
        # simple MongoDB ping
        client.admin.command('ping')
        
        return jsonify({
            "status": "ok",
            "database": "connected"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
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
    from dotenv import load_dotenv
    load_dotenv()
    app.run(debug=True, port=3000)
