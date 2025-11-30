from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client['hospital_db'] # You can name your DB

users_collection = db['users'] # A 'users' collection

print("MongoDB connection successful")
