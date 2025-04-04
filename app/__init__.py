from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import posthog
load_dotenv() 

# Initialize the Flask application
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/mydatabase")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key") 

# Initialize PostHog if API key is available
posthog_api_key = os.getenv('POSTHOG_API_KEY')
if posthog_api_key:
    posthog.api_key = posthog_api_key
    posthog.host = os.getenv('POSTHOG_HOST', 'https://app.posthog.com')

# Initialize PyMongo for MongoDB interactions
mongo = PyMongo(app)

# Ensure database is initialized
with app.app_context():
    # Create collections if they don't exist
    if 'users' not in mongo.db.list_collection_names():
        mongo.db.create_collection('users')
    if 'expenses' not in mongo.db.list_collection_names():
        mongo.db.create_collection('expenses')
    if 'user_settings' not in mongo.db.list_collection_names():
        mongo.db.create_collection('user_settings')

# Initialize the LoginManager for user session management
login_manager = LoginManager(app)
# Set the login view for the application
login_manager.login_view = 'login'

# Import routes after initializing the app to avoid circular imports
from app import routes
