import pytest
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import login_user
from werkzeug.security import generate_password_hash
from app import app as flask_app
from app.models import User

@pytest.fixture()
def app():
    # Configure the Flask app for testing
    flask_app.config.update({
        'TESTING': True,  
        'WTF_CSRF_ENABLED': False, 
    })
    return flask_app  # Returns the app instance

# Providing a test client to make requests
@pytest.fixture
def client(app):
    return app.test_client()  # Returns a test client

# Initialize and provide access to PyMongo
@pytest.fixture
def mongo(app):
    return PyMongo(app) 

# Create a test user for the database
@pytest.fixture
def test_user(mongo):
    user_data = {
        'email': 'test@example.com',
        'password': generate_password_hash('password123') 
    }
    mongo.db.users.delete_many({'email': user_data['email']})
    # Making sure there is only one user
    result = mongo.db.users.insert_one(user_data)
    user_data['_id'] = result.inserted_id  
    return user_data  # Return the test user data

# Do a logged-in user session
@pytest.fixture
def auth_client(client, test_user, app):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user['_id'])  # Set the session

    with app.test_request_context():
        # Initialize a User object
        user = User(test_user['_id'])
        login_user(user)

    return client  # Return the authenticated test client