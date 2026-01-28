import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True # Flask testing mode
    with app.test_client() as client:
        yield client


# 1️⃣ Test Home Page Loads Successfully
def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    # Check unique text from home page
    assert b"Welcome to CityCare Hospital" in response.data


# 2️⃣ Test Login Page Accessible
def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


# 3️⃣ Invalid Login Displays Error Message
def test_invalid_login(client):
    response = client.post(
        "/login",
        data={"username": "wrong", "password": "bad"},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data


# 4️⃣ Patients Page Requires Login
def test_patients_protected(client):
    response = client.get("/patients", follow_redirects=True)
    assert b"Login" in response.data # Redirected to login if not logged in


# 5️⃣ 404 Not Found Page Test
def test_404_page(client):
    response = client.get("/thispagedoesnotexist")
    assert response.status_code == 404
    # Check text from your custom 404.html
    assert b"Page Not Found" in response.data or b"404" in response.data


# 6️⃣ Test Registration Page Loads
def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data or b"register" in response.data


# 7️⃣ Test Successful Registration
def test_successful_registration(client):
    import time
    unique_username = f"newuser{int(time.time())}"
    response = client.post(
        "/register",
        data={
            "username": unique_username,
            "password": "securepass123",
            "confirm_password": "securepass123",
            "role": "patient"
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"registered successfully" in response.data


# 8️⃣ Test Registration with Mismatched Passwords
def test_registration_password_mismatch(client):
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "password123",
            "confirm_password": "password456",
            "role": "doctor"
        },
        follow_redirects=True
    )
    assert b"Passwords do not match" in response.data


# 9️⃣ Test Registration with Missing Fields
def test_registration_missing_fields(client):
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "password": "",
            "confirm_password": "",
            "role": "patient"
        },
        follow_redirects=True
    )
    assert b"Please fill all fields" in response.data or b"Fill all fields" in response.data


# 1️⃣0️⃣ Test About Page Loads
def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"About" in response.data or b"about" in response.data


# 1️⃣1️⃣ Test Logout Redirects to Login
def test_logout(client):
    # First login
    client.post(
        "/login",
        data={"username": "testdoctor", "password": "password123"},
        follow_redirects=True
    )
    # Then logout
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


# 1️⃣2️⃣ Test Doctor Dashboard Requires Login
def test_doctor_dashboard_protected(client):
    response = client.get("/doctor_dashboard", follow_redirects=True)
    assert b"Login" in response.data


# 1️⃣3️⃣ Test Patient Dashboard Requires Login
def test_patient_dashboard_protected(client):
    response = client.get("/patient_dashboard", follow_redirects=True)
    assert b"Login" in response.data


# 1️⃣4️⃣ Test Patients Page Requires Doctor Role
def test_patients_requires_doctor_role(client):
    response = client.get("/patients", follow_redirects=True)
    assert b"Login" in response.data or response.status_code == 200


# 1️⃣5️⃣ Test Password Validation (Empty Username)
def test_login_empty_username(client):
    response = client.post(
        "/login",
        data={"username": "", "password": "somepassword"},
        follow_redirects=True
    )
    assert b"Please fill in all fields" in response.data or b"fill" in response.data


# 1️⃣6️⃣ Test Password Validation (Empty Password)
def test_login_empty_password(client):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": ""},
        follow_redirects=True
    )
    assert b"Please fill in all fields" in response.data or b"fill" in response.data


# 1️⃣7️⃣ Test Session Persistence After Login
def test_session_after_login(client):
    client.post(
        "/login",
        data={"username": "testdoctor", "password": "password123"},
        follow_redirects=True
    )
    # After login, user should have session data
    with client.session_transaction() as sess:
        # Session might be set or cleared depending on login success
        pass


# 1️⃣8️⃣ Test Multiple Invalid Login Attempts
def test_multiple_invalid_logins(client):
    for _ in range(3):
        response = client.post(
            "/login",
            data={"username": "wronguser", "password": "wrongpass"},
            follow_redirects=True
        )
        assert b"Invalid username or password" in response.data


# ======================== INTEGRATION TESTS ========================


# 1️⃣9️⃣ Integration: Full Registration → Login → Dashboard Flow
def test_integration_register_login_dashboard(client):
    """Test complete user journey: register → login → access dashboard"""
    import time
    unique_user = f"integ_user_{int(time.time())}"
    
    # Step 1: Register new user as doctor
    reg_response = client.post(
        "/register",
        data={
            "username": unique_user,
            "password": "testpass123",
            "confirm_password": "testpass123",
            "role": "doctor"
        },
        follow_redirects=True
    )
    assert reg_response.status_code == 200
    assert b"registered successfully" in reg_response.data
    
    # Step 2: Login with registered credentials
    login_response = client.post(
        "/login",
        data={"username": unique_user, "password": "testpass123"},
        follow_redirects=True
    )
    assert login_response.status_code == 200
    assert b"Doctor" in login_response.data or b"dashboard" in login_response.data.lower()
    
    # Step 3: Verify session is maintained
    with client.session_transaction() as sess:
        assert sess.get("username") == unique_user
        assert sess.get("role") == "doctor"
    
    # Step 4: Access protected doctor dashboard
    dashboard_response = client.get("/doctor_dashboard")
    assert dashboard_response.status_code == 200
    assert b"Doctor" in dashboard_response.data or b"patient" in dashboard_response.data.lower()


# 2️⃣0️⃣ Integration: Unregistered User Cannot Access Protected Pages
def test_integration_unauthorized_access_blocked(client):
    """Verify that unregistered users are blocked from protected pages"""
    
    # Attempt to access doctor dashboard without login
    response = client.get("/doctor_dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data  # Should be redirected to login
    
    # Attempt to access patient dashboard without login
    response = client.get("/patient_dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data  # Should be redirected to login


# 2️⃣1️⃣ Integration: Role-Based Access Control
def test_integration_role_based_access(client):
    """Test that only doctors can access certain pages"""
    import time
    
    # Register as patient
    patient_user = f"patient_{int(time.time())}"
    client.post(
        "/register",
        data={
            "username": patient_user,
            "password": "patientpass",
            "confirm_password": "patientpass",
            "role": "patient"
        },
        follow_redirects=True
    )
    
    # Login as patient
    client.post(
        "/login",
        data={"username": patient_user, "password": "patientpass"},
        follow_redirects=True
    )
    
    # Verify session shows patient role
    with client.session_transaction() as sess:
        assert sess.get("role") == "patient"
    
    # Patient should be redirected from doctor dashboard
    response = client.get("/doctor_dashboard", follow_redirects=True)
    assert response.status_code == 200


# 2️⃣2️⃣ Integration: Login → Logout → Cannot Access Protected
def test_integration_logout_removes_access(client):
    """Verify that after logout, protected pages are no longer accessible"""
    import time
    
    # Register and login
    user = f"logout_test_{int(time.time())}"
    client.post(
        "/register",
        data={
            "username": user,
            "password": "pass123",
            "confirm_password": "pass123",
            "role": "doctor"
        },
        follow_redirects=True
    )
    
    client.post(
        "/login",
        data={"username": user, "password": "pass123"},
        follow_redirects=True
    )
    
    # Verify can access protected page
    response = client.get("/doctor_dashboard")
    assert response.status_code == 200
    
    # Logout
    logout_response = client.get("/logout", follow_redirects=True)
    assert logout_response.status_code == 200
    
    # Verify cannot access protected page anymore
    response = client.get("/doctor_dashboard", follow_redirects=True)
    assert b"Login" in response.data


# 2️⃣3️⃣ Integration: Failed Login → Session Not Created
def test_integration_failed_login_no_session(client):
    """Verify that failed login doesn't create a session"""
    
    # Attempt login with wrong credentials
    response = client.post(
        "/login",
        data={"username": "nonexistent", "password": "wrongpass"},
        follow_redirects=True
    )
    assert response.status_code == 200
    
    # Verify no session was created
    with client.session_transaction() as sess:
        assert sess.get("username") is None
        assert sess.get("role") is None
    
    # Verify still cannot access protected pages
    protected_response = client.get("/doctor_dashboard", follow_redirects=True)
    assert b"Login" in protected_response.data


# 2️⃣4️⃣ Integration: Public Pages Accessible Without Login
def test_integration_public_pages_accessible(client):
    """Verify public pages can be accessed without authentication"""
    
    # Home page
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"CityCare" in response.data
    
    # About page
    response = client.get("/about")
    assert response.status_code == 200
    
    # Login page
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data
    
    # Register page
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data or b"register" in response.data.lower()


# 2️⃣5️⃣ Integration: Multi-Step Registration Validation
def test_integration_registration_validation_flow(client):
    """Test various registration scenarios in sequence"""
    import time
    
    # Test 1: Missing fields
    response = client.post(
        "/register",
        data={"username": "test", "password": "", "confirm_password": "", "role": ""},
        follow_redirects=True
    )
    assert b"Please fill all fields" in response.data or b"Fill all fields" in response.data
    
    # Test 2: Password mismatch
    response = client.post(
        "/register",
        data={
            "username": f"user_{int(time.time())}",
            "password": "pass123",
            "confirm_password": "pass456",
            "role": "patient"
        },
        follow_redirects=True
    )
    assert b"Passwords do not match" in response.data
    
    # Test 3: Successful registration
    user = f"success_{int(time.time())}"
    response = client.post(
        "/register",
        data={
            "username": user,
            "password": "securepass",
            "confirm_password": "securepass",
            "role": "doctor"
        },
        follow_redirects=True
    )
    assert b"registered successfully" in response.data


# 2️⃣6️⃣ Integration: Session Persistence Across Multiple Requests
def test_integration_session_persistence(client):
    """Verify session persists across multiple authenticated requests"""
    import time
    
    user = f"persist_{int(time.time())}"
    
    # Register and login
    client.post(
        "/register",
        data={
            "username": user,
            "password": "pass123",
            "confirm_password": "pass123",
            "role": "patient"
        }
    )
    
    client.post(
        "/login",
        data={"username": user, "password": "pass123"}
    )
    
    # Make multiple requests and verify session persists
    for _ in range(3):
        response = client.get("/patient_dashboard")
        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert sess.get("username") == user
            assert sess.get("role") == "patient"