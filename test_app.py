import unittest
from app import app

class BasicTests(unittest.TestCase):

    def setUp(self):
        # Create a test client before each test
        self.app = app.test_client()

    # Check if the home page loads correctly
    def test_home_page(self):
        response = self.app.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Check if the about page loads correctly
    def test_about_page(self):
        response = self.app.get('/about', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Check if the register page loads correctly
    def test_register_page(self):
        response = self.app.get('/register', content_type='html/text')
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()