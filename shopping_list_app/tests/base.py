import unittest
from shopping_list_app.wsgi import app # Adjusted import assuming tests run from /app or PYTHONPATH includes /app
from shopping_list_app.app.extensions import db
from shopping_list_app.app.models import User, Household, ShoppingList, ShoppingItem # Import all models

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Configure the app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory SQLite for tests
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF forms for testing
        app.config['SECRET_KEY'] = 'test_secret_key' # Needs a secret key for sessions, flash messages
        # app.config['LOGIN_DISABLED'] = True # Optional: Disable login for tests not focusing on auth.
                                          # For now, keep it False to test auth flows.

        self.app_context = app.app_context()
        self.app_context.push() # Push an application context
        db.create_all() # Create all tables

        self.client = app.test_client() # Flask test client

    def tearDown(self):
        db.session.remove()
        db.drop_all() # Drop all tables
        self.app_context.pop() # Pop the application context

    # Helper method to create a user
    def create_user(self, username="testuser", email="test@example.com", password="password"):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    # Helper method to register a user via form
    def register_user(self, username, email, password, confirm_password):
        return self.client.post('/register', data=dict(
            username=username,
            email=email,
            password=password,
            confirm_password=confirm_password
        ), follow_redirects=True)

    # Helper method to login a user
    def login_user(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    # Helper method to logout a user
    def logout_user(self):
        return self.client.get('/logout', follow_redirects=True)
