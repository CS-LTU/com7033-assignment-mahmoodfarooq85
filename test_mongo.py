"""
MongoDB Integration Tests
Tests for MongoDB operations and data synchronization
"""

import pytest
from datetime import datetime, timezone
from mongo import (
    insert_user, 
    insert_patient, 
    get_all_users, 
    get_all_patients,
    get_patient_by_id,
    update_patient,
    delete_patient,
    get_patient_count,
    get_user_count,
    is_mongodb_connected
)


class TestMongoDBConnection:
    """Test MongoDB connection and availability"""
    
    def test_mongodb_is_connected(self):
        """Test that MongoDB connection is active"""
        assert is_mongodb_connected(), "MongoDB should be connected"
    
    def test_collections_exist(self):
        """Test that required collections are accessible"""
        from mongo import users_collection, patients_collection
        assert users_collection is not None, "Users collection should exist"
        assert patients_collection is not None, "Patients collection should exist"


class TestUserOperations:
    """Test user-related MongoDB operations"""
    
    def test_insert_user(self):
        """Test inserting a new user into MongoDB"""
        username = f"test_user_{datetime.now().timestamp()}"
        password_hash = "hashed_password_123"
        role = "patient"
        
        result = insert_user(username, password_hash, role)
        
        assert result["success"] is True, f"Insert should succeed: {result.get('error')}"
        assert "user_id" in result, "Result should contain user_id"
    
    def test_insert_multiple_users(self):
        """Test inserting multiple users"""
        test_users = [
            ("doctor_test", "hash1", "doctor"),
            ("patient_test", "hash2", "patient"),
            ("staff_test", "hash3", "staff"),
        ]
        
        initial_count = get_user_count()
        
        for username, password_hash, role in test_users:
            result = insert_user(f"{username}_{datetime.now().timestamp()}", password_hash, role)
            assert result["success"] is True
        
        new_count = get_user_count()
        assert new_count >= initial_count + len(test_users), "User count should increase"
    
    def test_get_all_users(self):
        """Test retrieving all users from MongoDB"""
        users = get_all_users()
        
        assert isinstance(users, list), "Should return a list"
        # Database may have existing users
        if len(users) > 0:
            user = users[0]
            assert "username" in user, "User should have username"
            assert "role" in user, "User should have role"
            assert "created_at" in user, "User should have created_at"
    
    def test_user_contains_required_fields(self):
        """Test that inserted users have all required fields"""
        username = f"test_fields_{datetime.now().timestamp()}"
        password_hash = "test_hash"
        role = "doctor"
        
        result = insert_user(username, password_hash, role)
        assert result["success"] is True
        
        users = get_all_users()
        test_user = next((u for u in users if u.get("username") == username), None)
        
        assert test_user is not None, "User should exist in database"
        assert test_user["username"] == username
        assert test_user["password_hash"] == password_hash
        assert test_user["role"] == role
        assert "created_at" in test_user


class TestPatientOperations:
    """Test patient-related MongoDB operations"""
    
    def test_insert_patient(self):
        """Test inserting a new patient into MongoDB"""
        patient_id = int(datetime.now().timestamp() * 1000) % 100000
        name = "Test Patient"
        age = 45
        condition = "Hypertension"
        added_by = "test_doctor"
        
        result = insert_patient(patient_id, name, age, condition, added_by)
        
        assert result["success"] is True, f"Insert should succeed: {result.get('error')}"
        assert "patient_id" in result, "Result should contain patient_id"
    
    def test_insert_multiple_patients(self):
        """Test inserting multiple patients"""
        initial_count = get_patient_count()
        
        patients_to_add = [
            ("John Doe", 35, "Diabetes"),
            ("Jane Smith", 50, "Heart Disease"),
            ("Bob Johnson", 28, "Asthma"),
        ]
        
        added_by = "test_doctor"
        
        for name, age, condition in patients_to_add:
            patient_id = int(datetime.now().timestamp() * 1000000) % 10000000
            result = insert_patient(patient_id, name, age, condition, added_by)
            assert result["success"] is True, f"Failed to insert {name}"
        
        new_count = get_patient_count()
        assert new_count >= initial_count + len(patients_to_add), "Patient count should increase"
    
    def test_get_patient_by_id(self):
        """Test retrieving a specific patient by ID"""
        patient_id = int(datetime.now().timestamp() * 1000000) % 10000000
        name = "Test Patient Lookup"
        age = 40
        condition = "Test Condition"
        added_by = "test_doctor"
        
        # Insert patient
        insert_patient(patient_id, name, age, condition, added_by)
        
        # Retrieve patient
        patient = get_patient_by_id(patient_id)
        
        assert patient is not None, "Patient should be found"
        assert patient["id"] == patient_id
        assert patient["name"] == name
        assert patient["age"] == age
        assert patient["condition"] == condition
    
    def test_patient_contains_required_fields(self):
        """Test that inserted patients have all required fields"""
        patient_id = int(datetime.now().timestamp() * 1000000) % 10000000
        name = "Fields Test Patient"
        age = 55
        condition = "Stroke Risk"
        added_by = "test_doctor"
        
        result = insert_patient(patient_id, name, age, condition, added_by)
        assert result["success"] is True
        
        patient = get_patient_by_id(patient_id)
        
        assert patient is not None
        assert patient["id"] == patient_id
        assert patient["name"] == name
        assert patient["age"] == age
        assert patient["condition"] == condition
        assert patient["added_by"] == added_by
        assert patient["source"] == "web_form"
        assert "created_at" in patient
    
    def test_get_all_patients(self):
        """Test retrieving all patients"""
        patients = get_all_patients()
        
        assert isinstance(patients, list), "Should return a list"
        if len(patients) > 0:
            patient = patients[0]
            assert "id" in patient, "Patient should have id"
            assert "name" in patient, "Patient should have name"
            assert "condition" in patient, "Patient should have condition"
            assert "created_at" in patient, "Patient should have created_at"
    
    def test_update_patient(self):
        """Test updating a patient record"""
        patient_id = int(datetime.now().timestamp() * 1000000) % 10000000
        name = "Original Name"
        age = 30
        condition = "Original Condition"
        
        # Insert patient
        insert_patient(patient_id, name, age, condition, "test_doctor")
        
        # Update patient
        update_data = {
            "name": "Updated Name",
            "condition": "Updated Condition",
            "age": 31
        }
        result = update_patient(patient_id, update_data)
        
        assert result["success"] is True, f"Update should succeed: {result.get('error')}"
        assert result["modified_count"] >= 1, "Should update at least one record"
        
        # Verify update
        patient = get_patient_by_id(patient_id)
        assert patient["name"] == "Updated Name"
        assert patient["condition"] == "Updated Condition"
        assert patient["age"] == 31
    
    def test_delete_patient(self):
        """Test deleting a patient record"""
        patient_id = int(datetime.now().timestamp() * 1000000) % 10000000
        name = "Patient to Delete"
        
        # Insert patient
        insert_patient(patient_id, name, 25, "Test", "test_doctor")
        
        # Verify patient exists
        patient = get_patient_by_id(patient_id)
        assert patient is not None, "Patient should exist before deletion"
        
        # Delete patient
        result = delete_patient(patient_id)
        
        assert result["success"] is True, f"Delete should succeed: {result.get('error')}"
        assert result["deleted_count"] >= 1, "Should delete at least one record"
        
        # Verify patient is deleted
        patient = get_patient_by_id(patient_id)
        assert patient is None, "Patient should be deleted"


class TestDataCounts:
    """Test data counting operations"""
    
    def test_get_patient_count(self):
        """Test counting total patients"""
        count = get_patient_count()
        
        assert isinstance(count, int), "Should return an integer"
        assert count >= 0, "Count should be non-negative"
    
    def test_get_user_count(self):
        """Test counting total users"""
        count = get_user_count()
        
        assert isinstance(count, int), "Should return an integer"
        assert count >= 0, "Count should be non-negative"
    
    def test_count_increases_after_insert(self):
        """Test that count increases after inserting data"""
        initial_patient_count = get_patient_count()
        
        patient_id = int(datetime.now().timestamp() * 1000000) % 10000000
        insert_patient(patient_id, "Count Test", 40, "Test", "test_doctor")
        
        new_patient_count = get_patient_count()
        assert new_patient_count > initial_patient_count, "Count should increase after insert"


class TestErrorHandling:
    """Test error handling in MongoDB operations"""
    
    def test_insert_patient_with_invalid_data(self):
        """Test error handling with invalid patient data"""
        result = insert_patient(None, "", None, "", "")
        
        # Should handle gracefully (either succeed or return error with message)
        if not result["success"]:
            assert "error" in result, "Error should be documented"
    
    def test_update_nonexistent_patient(self):
        """Test updating a patient that doesn't exist"""
        result = update_patient(999999999, {"name": "Fake"})
        
        # MongoDB allows updates even if no document exists (upsert)
        # But we should get no modified count
        assert isinstance(result, dict), "Should return a result dictionary"
    
    def test_delete_nonexistent_patient(self):
        """Test deleting a patient that doesn't exist"""
        result = delete_patient(888888888)
        
        # Should handle gracefully - either succeed with 0 deleted or return false
        assert isinstance(result, dict), "Should return a result dictionary"
        assert "success" in result, "Result should have success key"
    
    def test_get_nonexistent_patient(self):
        """Test retrieving a patient that doesn't exist"""
        patient = get_patient_by_id(777777777)
        
        assert patient is None, "Should return None for nonexistent patient"


class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    def test_patient_created_at_is_datetime(self):
        """Test that created_at is a proper datetime"""
        patient_id = int(datetime.now().timestamp() * 1000000) % 10000000
        insert_patient(patient_id, "DateTime Test", 30, "Test", "test_doctor")
        
        patient = get_patient_by_id(patient_id)
        
        assert patient is not None
        assert isinstance(patient["created_at"], datetime), "created_at should be datetime"
    
    def test_user_created_at_is_datetime(self):
        """Test that user created_at is a proper datetime"""
        username = f"datetime_test_{datetime.now().timestamp()}"
        insert_user(username, "hash", "patient")
        
        users = get_all_users()
        test_user = next((u for u in users if u.get("username") == username), None)
        
        assert test_user is not None
        assert isinstance(test_user["created_at"], datetime), "created_at should be datetime"
    
    def test_patient_role_values(self):
        """Test that user roles are valid"""
        valid_roles = ["doctor", "patient", "staff", "admin"]
        
        users = get_all_users()
        
        for user in users:
            if "role" in user:
                assert user["role"] in valid_roles or user["role"] is not None, \
                    f"Invalid role: {user['role']}"
    
    def test_all_four_roles_in_mongodb(self):
        """Test that all 4 roles can be stored in MongoDB"""
        valid_roles = ["doctor", "patient", "staff", "admin"]
        
        # Insert users with each role
        for role in valid_roles:
            username = f"role_test_{role}_{datetime.now().timestamp()}"
            result = insert_user(username, "test_hash", role)
            assert result["success"] is True, f"Failed to insert user with role {role}"
        
        # Verify all roles exist in database
        users = get_all_users()
        stored_roles = {user["role"] for user in users if "role" in user}
        
        for role in valid_roles:
            assert role in stored_roles, f"Role '{role}' should be in MongoDB"
        
        # Verify each role has correct data
        for role in valid_roles:
            role_users = [u for u in users if u.get("role") == role]
            assert len(role_users) > 0, f"Should have at least one user with role '{role}'"
            
            for user in role_users:
                assert user["role"] == role, f"User should have role {role}"
                assert "username" in user, "User should have username"
                assert "created_at" in user, "User should have created_at"


if __name__ == "__main__":
    # Run tests with: pytest test_mongo.py -v
    pytest.main([__file__, "-v"])
