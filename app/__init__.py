from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize PyMongo for MongoDB interactions
mongo = PyMongo(app)

# Initialize the LoginManager for user session management
login_manager = LoginManager(app)
# Set the login view for the application
login_manager.login_view = 'login'

# Import routes after initializing the app to avoid circular imports
from app import routes
