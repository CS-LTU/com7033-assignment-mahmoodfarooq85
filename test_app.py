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