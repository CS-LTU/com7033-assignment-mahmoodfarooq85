from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

try:
    client = MongoClient(MONGO_URI)
    db = client["hospital_db"] # database name
    users_collection = db["users"] # collection name
    print("MongoDB connection successful!")
except Exception as e:
    print("MongoDB connection failed:", e)
