import pytest
from flask import Flask
from flask_pymongo import PyMongo
from flask_login import login_user
from werkzeug.security import generate_password_hash
from app import app as flask_app
from app.models import User
from datetime import datetime
from bson import ObjectId
from mongomock import MongoClient

@pytest.fixture()
def app():
    """Create and configure a Flask application for testing."""
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'MONGO_URI': 'mongodb://localhost:27017/test_db'
    })
    return flask_app

@pytest.fixture()
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture()
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def mock_db():
    """Create a mock database."""
    client = MongoClient()
    db = client.test_db
    
    # Initialize collections
    db.users.create_index('email', unique=True)
    db.expenses.create_index([('user_id', 1), ('date', -1)])
    
    return db

@pytest.fixture
def test_user(mock_db):
    """Create a test user with initial settings."""
    user_data = {
        '_id': ObjectId(),
        'email': 'test@example.com',
        'password': 'password123',
        'created_at': datetime.now(),
        'budget_settings': {
            'needs': 50,
            'wants': 30,
            'savings': 10,
            'investments': 10
        },
        'savings_goals': []
    }
    mock_db.users.insert_one(user_data)
    return user_data

class MockPyMongo:
    def __init__(self, db):
        self.db = db

@pytest.fixture
def mongo(mock_db):
    """Create a mock PyMongo instance."""
    return MockPyMongo(mock_db)

@pytest.fixture
def auth_client(client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as session:
        session['_user_id'] = str(test_user['_id'])
        session['_fresh'] = True
    return client

@pytest.fixture(autouse=True)
def app_context(app):
    """Create an application context for testing."""
    with app.app_context():
        yield

@pytest.fixture(autouse=True)
def override_mongo(app, monkeypatch, mongo):
    """Override the MongoDB connection to use the mock database."""
    def mock_init_app(self, app):
        self.db = mongo.db
        return self
    
    monkeypatch.setattr('flask_pymongo.PyMongo.init_app', mock_init_app)
    monkeypatch.setattr('app.mongo.db', mongo.db)
    
    with app.app_context():
        yield mongo