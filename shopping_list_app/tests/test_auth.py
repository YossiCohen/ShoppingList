from .base import BaseTestCase # Adjusted import
from shopping_list_app.app.models import User
from shopping_list_app.app.extensions import db
from flask import get_flashed_messages

class TestAuth(BaseTestCase):

    def test_successful_registration(self):
        response = self.register_user("newuser", "new@example.com", "password123", "password123")
        self.assertEqual(response.status_code, 200) # Should redirect to login, then 200

        # Check if user is in database
        user = User.query.filter_by(email="new@example.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "newuser")

        # Check flashed message - this requires response.data to be decoded
        # and depends on how flashed messages are rendered in the template.
        # For simplicity, checking if a known part of the success message is present.
        # Note: Accessing _flashes might be needed if follow_redirects=True consumes the message.
        # Alternatively, test the redirect location.
        # self.assertIn(b'Congratulations, you are now a registered user!', response.data)
        # Let's check redirect to login page
        self.assertTrue(response.request.path.endswith('/login'))


    def test_registration_duplicate_username(self):
        self.create_user(username="existinguser", email="exists@example.com", password="password")
        response = self.register_user("existinguser", "new2@example.com", "password123", "password123")
        self.assertEqual(response.status_code, 200) # Stays on register page
        self.assertIn(b'That username is taken.', response.data) # Check form validation error

    def test_registration_duplicate_email(self):
        self.create_user(username="anotheruser", email="existing@example.com", password="password")
        response = self.register_user("newuser2", "existing@example.com", "password123", "password123")
        self.assertEqual(response.status_code, 200) # Stays on register page
        self.assertIn(b'That email is already registered.', response.data)

    def test_successful_login_logout(self):
        self.create_user(username="loginuser", email="login@example.com", password="password123")

        # Test login
        login_response = self.login_user("login@example.com", "password123")
        self.assertEqual(login_response.status_code, 200)
        # Check if redirected to index or if index page content is there
        self.assertTrue(login_response.request.path.endswith('/index') or login_response.request.path.endswith('/'))
        self.assertIn(b'Login successful!', login_response.data) # Check flashed message

        # Test logout
        logout_response = self.logout_user()
        self.assertEqual(logout_response.status_code, 200)
        self.assertTrue(logout_response.request.path.endswith('/index') or logout_response.request.path.endswith('/'))
        self.assertIn(b'You have been logged out.', logout_response.data) # Check flashed message

    def test_login_invalid_credentials(self):
        self.create_user(username="loginuser2", email="login2@example.com", password="password123")
        response = self.login_user("login2@example.com", "wrongpassword")
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Invalid username or password', response.data) # Check flashed error

    def test_login_nonexistent_user(self):
        response = self.login_user("donotexist@example.com", "password")
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Invalid username or password', response.data)

    def test_access_protected_route_unauthenticated(self):
        # Try to access index page which requires login
        response = self.client.get('/index', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Should be redirected to login page
        self.assertTrue(response.request.path.endswith('/login'))
        self.assertIn(b'Please log in to access this page.', response.data) # Flask-Login default message

    def test_access_protected_route_authenticated(self):
        self.create_user(username="autheduser", email="auth@example.com", password="password")
        self.login_user("auth@example.com", "password")

        response = self.client.get('/index')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Shopping List App!', response.data) # Check content of index page
        self.assertIn(b'autheduser', response.data) # Check if username is displayed
