from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Basic login manager configuration
login_manager.login_view = 'main.login' # Corrected to main blueprint's login route
login_manager.login_message_category = 'info'

# User loader function for Flask-Login
# This needs to be here or imported after User model is defined,
# but to avoid circular imports with models.py, it's often placed
# in the main app factory or here, and models are imported carefully.
# For now, we'll define it and it will expect the User model later.
@login_manager.user_loader
def load_user(user_id):
    # Import User model locally to avoid circular dependency if models imports db from here
    from .models import User
    return User.query.get(int(user_id))
