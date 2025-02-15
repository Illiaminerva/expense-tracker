from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
load_dotenv() 

# Initialize the Flask application
app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/mydatabase")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key") 


# Initialize PyMongo for MongoDB interactions
mongo = PyMongo(app)

# Initialize the LoginManager for user session management
login_manager = LoginManager(app)
# Set the login view for the application
login_manager.login_view = 'login'

# Import routes after initializing the app to avoid circular imports
from app import routes
