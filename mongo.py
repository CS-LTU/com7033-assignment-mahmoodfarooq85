import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Configure logging
logging.basicConfig(filename="mongo.log", level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "hospital_db")

# Initialize MongoDB connection with error handling
client = None
db = None
users_collection = None
patients_collection = None

def connect_to_mongodb():
    """
    Establish MongoDB connection with proper error handling and logging.
    Returns: tuple (client, db, users_collection, patients_collection)
    """
    global client, db, users_collection, patients_collection
    
    try:
        if not MONGO_URI:
            logger.error("MONGO_URI not configured in environment variables")
            print("⚠️ ERROR: MONGO_URI not configured")
            return None, None, None, None
        
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command("ping")
        logger.info("✓ MongoDB connection established successfully")
        print("✓ MongoDB connection OK")
        
        # Get database and collections
        db = client[DB_NAME]
        users_collection = db["users"]
        patients_collection = db["patients"]
        
        # Create indexes for better performance
        create_indexes()
        
        return client, db, users_collection, patients_collection
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB connection failed: {e}")
        print(f"⚠️ MongoDB connection failed: {e}")
        return None, None, None, None
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        print(f"⚠️ Unexpected error: {e}")
        return None, None, None, None

def create_indexes():
    """Create indexes for optimal query performance."""
    try:
        # Users collection indexes
        users_collection.create_index("username", unique=True)
        users_collection.create_index("role")
        users_collection.create_index("created_at")
        
        # Patients collection indexes
        patients_collection.create_index("id", unique=True)
        patients_collection.create_index("name")
        patients_collection.create_index("added_by")
        patients_collection.create_index("created_at")
        
        logger.info("✓ Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")

def is_mongodb_connected():
    """
    Check if MongoDB connection is active.
    Returns: bool
    """
    try:
        if client:
            client.admin.command("ping")
            return True
    except Exception:
        pass
    return False

def insert_user(username, password_hash, role):
    """
    Insert a new user into MongoDB.
    Returns: dict with result info
    """
    try:
        if users_collection is None:
            return {"success": False, "error": "MongoDB not connected"}
        
        from datetime import datetime, timezone
        user_doc = {
            "username": username,
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.now(timezone.utc)
        }
        
        result = users_collection.insert_one(user_doc)
        logger.info(f"✓ User '{username}' inserted into MongoDB - ID: {result.inserted_id}")
        return {"success": True, "user_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error inserting user '{username}': {e}")
        return {"success": False, "error": str(e)}

def insert_patient(patient_id, name, age, condition, added_by):
    """
    Insert a new patient into MongoDB.
    Returns: dict with result info
    """
    try:
        if patients_collection is None:
            return {"success": False, "error": "MongoDB not connected"}
        
        from datetime import datetime, timezone
        patient_doc = {
            "id": patient_id,
            "name": name,
            "age": age,
            "condition": condition,
            "created_at": datetime.now(timezone.utc),
            "added_by": added_by,
            "source": "web_form"
        }
        
        result = patients_collection.insert_one(patient_doc)
        logger.info(f"✓ Patient '{name}' (ID: {patient_id}) inserted by '{added_by}'")
        return {"success": True, "patient_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error inserting patient '{name}': {e}")
        return {"success": False, "error": str(e)}

def get_all_users():
    """Get all users from MongoDB."""
    try:
        if users_collection is None:
            return []
        return list(users_collection.find({}, {"_id": 0}))
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []

def get_all_patients():
    """Get all patients from MongoDB."""
    try:
        if patients_collection is None:
            return []
        return list(patients_collection.find({}, {"_id": 0}).sort("created_at", -1))
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        return []

def get_patient_by_id(patient_id):
    """Get a specific patient by ID."""
    try:
        if patients_collection is None:
            return None
        return patients_collection.find_one({"id": patient_id}, {"_id": 0})
    except Exception as e:
        logger.error(f"Error fetching patient ID {patient_id}: {e}")
        return None

def update_patient(patient_id, update_data):
    """Update a patient record."""
    try:
        if patients_collection is None:
            return {"success": False, "error": "MongoDB not connected"}
        
        result = patients_collection.update_one(
            {"id": patient_id},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            logger.info(f"✓ Patient ID {patient_id} updated")
            return {"success": True, "modified_count": result.modified_count}
        else:
            return {"success": False, "error": "Patient not found"}
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {e}")
        return {"success": False, "error": str(e)}

def delete_patient(patient_id):
    """Delete a patient record."""
    try:
        if patients_collection is None:
            return {"success": False, "error": "MongoDB not connected"}
        
        result = patients_collection.delete_one({"id": patient_id})
        if result.deleted_count > 0:
            logger.info(f"✓ Patient ID {patient_id} deleted")
            return {"success": True, "deleted_count": result.deleted_count}
        else:
            return {"success": False, "error": "Patient not found"}
    except Exception as e:
        logger.error(f"Error deleting patient {patient_id}: {e}")
        return {"success": False, "error": str(e)}

def get_patient_count():
    """Get total number of patients."""
    try:
        if patients_collection is None:
            return 0
        return patients_collection.count_documents({})
    except Exception as e:
        logger.error(f"Error counting patients: {e}")
        return 0

def get_user_count():
    """Get total number of users."""
    try:
        if users_collection is None:
            return 0
        return users_collection.count_documents({})
    except Exception as e:
        logger.error(f"Error counting users: {e}")
        return 0

# Initialize MongoDB connection on import
client, db, users_collection, patients_collection = connect_to_mongodb()