import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "hospital_db")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]

try:
    client.admin.command("ping")
    print("MongoDB connection OK")
except Exception as e:
    print("MongoDB connection failed:", e)