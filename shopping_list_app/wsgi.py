import os
from flask import Flask
from app.extensions import db, migrate, login_manager
from app import models # Ensure models are imported before routes if routes use them at import time indirectly.
from app import routes as main_routes_blueprint # Import the blueprint

# Create the Flask app instance
app = Flask(__name__, instance_relative_config=True)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key_here' # Add a secret key for session management etc.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(app.instance_path, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass # Already exists or other error

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)

# Register Blueprints
app.register_blueprint(main_routes_blueprint.bp)
# If you had other blueprints, register them here e.g.
# from app.some_other_feature import bp as other_bp
# app.register_blueprint(other_bp, url_prefix='/other')


# The main index route is now in routes.py, so this can be removed or commented out.
# @app.route('/')
# def hello_world():
#     return 'Hello, World! Database configured.'

if __name__ == '__main__':
    app.run(debug=True)
