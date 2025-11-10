import unittest
from app import app # import your Flask app object


class BasicTests(unittest.TestCase):
    def setUp(self):
        # Put the app in testing mode and create a test client
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_page_status_code(self):
        """Home page should load successfully (status code 200)."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_register_page_status_code(self):
        """Register page should load successfully."""
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_login_page_status_code(self):
        """Login page should load successfully."""
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()