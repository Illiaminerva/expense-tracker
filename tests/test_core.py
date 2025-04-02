import pytest
from flask import session
from datetime import datetime

def test_app_exists(app):
    """Test that the app exists"""
    assert app is not None

def test_app_is_testing(app):
    """Test that the app is in testing mode"""
    assert app.config['TESTING'] is True

def test_client_exists(client):
    """Test that the client exists"""
    assert client is not None

def test_home_redirects_to_login(client):
    """Test that the home page redirects to login when not authenticated"""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302  # Redirect status code
    
    # Follow the redirect
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

def test_login_page_accessible(client):
    """Test that the login page is accessible"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_register_page_accessible(client):
    """Test that the register page is accessible"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_nonexistent_route_returns_404(client):
    """Test that a nonexistent route returns a 404 status code"""
    response = client.get('/nonexistent_route')
    assert response.status_code == 404

def test_mock_db_setup(mock_db, test_user):
    """Test that the mock database is set up correctly"""
    # Check that the users collection exists and has the test user
    users = mock_db['users']
    found_user = users.find_one({'email': 'test@example.com'})
    assert found_user is not None
    assert found_user['budget_settings']['needs'] == 50
    assert found_user['budget_settings']['wants'] == 30
    
    # Check that the expenses collection exists
    expenses = mock_db['expenses']
    assert expenses is not None
    
    # Add test expenses
    test_expenses = [
        {
            'user_id': str(test_user['_id']),
            'description': 'Test Expense 1',
            'amount': 100,
            'category': 'Needs',
            'date': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'user_id': str(test_user['_id']),
            'description': 'Test Expense 2',
            'amount': 200,
            'category': 'Wants',
            'date': datetime.now().strftime('%Y-%m-%d')
        }
    ]
    expenses.insert_many(test_expenses)
    
    # Verify collections have correct indexes
    user_indexes = users.index_information()
    expense_indexes = expenses.index_information()
    
    assert 'email_1' in user_indexes  # Check email index exists
    assert 'user_id_1_date_-1' in expense_indexes  # Check compound index exists
    
    # Check that the user settings are in the users collection
    test_settings = found_user.get('budget_settings')
    assert test_settings is not None
    assert test_settings.get('needs') == 50
    assert test_settings.get('wants') == 30
    assert test_settings.get('savings') == 10
    assert test_settings.get('investments') == 10
    
    # Check that the expenses collection has the test expenses
    test_expenses = list(expenses.find({'user_id': str(test_user['_id'])}))
    assert len(test_expenses) >= 2
    categories = [exp['category'] for exp in test_expenses]
    assert 'Needs' in categories
    assert 'Wants' in categories 