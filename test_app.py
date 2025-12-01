import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# 1️⃣ Test Home Page Loads Successfully
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hospital Secure Web App" in response.data


# 2️⃣ Test Login Page Accessible
def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data


# 3️⃣ Invalid Login Shows Error
def test_invalid_login(client):
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    }, follow_redirects=True)

    assert b"Invalid username or password" in response.data


# 4️⃣ Access Control: Patients page must redirect if Not Logged In
def test_patients_protected(client):
    response = client.get('/patients', follow_redirects=True)
    assert b"Login" in response.data # Means redirect happened successfully


# 5️⃣ 404 Page Test
def test_404_page(client):
    response = client.get('/thispagedoesnotexist')
    assert response.status_code == 404
    assert b"Page Not Found" in response.data or b"404" in response.data