import unittest
from app import app

# This file is for testing my Flask web application pages, and to make sure that all my pages (Home, About, Register) are working fine.

class BasicTests(unittest.TestCase):

    # This test is to  check if the home page loads correctly
    def test_home_page(self):
        tester = app.test_client(self) # creates a fake browser to test my site
        response = tester.get('/', content_type='html/text') # visits home page
        self.assertEqual(response.status_code, 200) # 200 means page loaded successfully

    # This test to check if the about page loads correctly
    def test_about_page(self):
        tester = app.test_client(self)
        response = tester.get('/about', content_type='html/text') # visits about page
        self.assertEqual(response.status_code, 200)

    # This test is to check if the register page loads correctly
    def test_register_page(self):
        tester = app.test_client(self)
        response = tester.get('/register', content_type='html/text') # visits register page
        self.assertEqual(response.status_code, 200)

# This part runs the tests when I use the command in terminal
if __name__ == "__main__":
    unittest.main()
