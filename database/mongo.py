from flask_pymongo import PyMongo
import os

mongo = PyMongo()

def init_mongo(app):
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise RuntimeError("❌ MONGO_URI is not set")

    app.config["MONGO_URI"] = mongo_uri
    mongo.init_app(app)

    print("✅ MongoDB connected successfully")
