import pytest
import json
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def test_budget_settings_validation(auth_client):
    """Test budget settings validation rules."""
    response = auth_client.post('/budget_settings', data={
        'needs_percentage': 50,
        'wants_percentage': 30,
        'savings_percentage': 30,
        'investments_percentage': 20
    }, follow_redirects=True)
    assert b'The total percentages cannot exceed 100%' in response.data
    
    response = auth_client.post('/budget_settings', data={
        'needs_percentage': 40,
        'wants_percentage': 30,
        'savings_percentage': 20,
        'investments_percentage': 10
    }, follow_redirects=True)
    assert b'Budget settings updated successfully' in response.data

def test_budget_calculation(auth_client, mock_db, test_user):
    """Test budget calculations based on expenses."""
    expenses = [
        {
            'user_id': str(test_user['_id']),
            'description': 'Rent',
            'amount': 1000.00,
            'category': 'Needs',
            'date': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'user_id': str(test_user['_id']),
            'description': 'Entertainment',
            'amount': 200.00,
            'category': 'Wants',
            'date': datetime.now().strftime('%Y-%m-%d')
        }
    ]
    mock_db.expenses.insert_many(expenses)

    response = auth_client.get('/summary')
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    
    assert '1200.00' in content
    assert 'Needs (50%)' in content
    assert 'Wants (30%)' in content

def test_budget_settings_persistence(auth_client, mock_db, test_user):
    """Test budget settings persistence."""
    settings = {
        'needs_percentage': 45,
        'wants_percentage': 25,
        'savings_percentage': 20,
        'investments_percentage': 10
    }
    
    response = auth_client.post('/budget_settings', data=settings, follow_redirects=True)
    assert response.status_code == 200
    
    user = mock_db.users.find_one({'_id': test_user['_id']})
    assert user['budget_settings']['needs'] == 45
    assert user['budget_settings']['wants'] == 25
    assert user['budget_settings']['savings'] == 20
    assert user['budget_settings']['investments'] == 10
    
    response = auth_client.get('/budget_settings')
    content = response.data.decode('utf-8')
    assert '45' in content
    assert '25' in content

def test_budget_settings_defaults(auth_client, mock_db):
    """Test default budget settings."""
    response = auth_client.get('/budget_settings')
    assert response.status_code == 200
    assert b'50' in response.data  # Default needs percentage
    assert b'30' in response.data  # Default wants percentage
    assert b'10' in response.data  # Default savings percentage
    assert b'10' in response.data  # Default investments percentage

def test_budget_settings(auth_client, mock_db, test_user):
    """Test budget settings page and form submission"""
    response = auth_client.get('/budget_settings')
    assert response.status_code == 200
    assert b'Budget Settings' in response.data

def test_budget_validation(auth_client):
    """Test budget validation rules"""
    response = auth_client.post('/budget_settings', data={
        'needs_percentage': '150',  # Invalid percentage
        'wants_percentage': '30',
        'savings_percentage': '20'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'The total percentages cannot exceed 100%' in response.data

def test_category_budgets(auth_client, mock_db, test_user):
    """Test category budget tracking"""
    response = auth_client.post('/set_budget', data={
        'Housing': '1000',
        'Food': '500',
        'Transportation': '200'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    user = mock_db.users.find_one({'_id': test_user['_id']})
    assert 'budget_categories' in user
    assert user['budget_categories'].get('Housing') == 1000.0

def test_budget_summary(auth_client, mock_db, test_user):
    """Test budget summary calculations"""
    mock_db.expenses.insert_many([
        {
            'user_id': str(test_user['_id']),
            'amount': 500,
            'category': 'Housing',
            'date': datetime.now().strftime('%Y-%m-%d')
        },
        {
            'user_id': str(test_user['_id']),
            'amount': 300,
            'category': 'Food',
            'date': datetime.now().strftime('%Y-%m-%d')
        }
    ])
    
    response = auth_client.get('/summary')
    assert response.status_code == 200
    content = response.data.decode('utf-8')
    assert '800.00' in content #total amount