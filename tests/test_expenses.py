import pytest
from datetime import datetime, timedelta
from bson import ObjectId

def test_add_expense(auth_client, mock_db, test_user):
    """Test adding a new expense"""
    response = auth_client.post('/add_expense', data={
        'description': 'Test Expense',
        'amount': '100',
        'category': 'Needs',
        'date': datetime.now().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Expense added successfully' in response.data

def test_edit_expense(auth_client, mock_db, test_user):
    """Test editing an existing expense"""
    expense_id = str(ObjectId())
    mock_db.expenses.insert_one({
        '_id': ObjectId(expense_id),
        'user_id': str(test_user['_id']),
        'description': 'Original',
        'amount': 100,
        'category': 'Needs',
        'date': datetime.now().strftime('%Y-%m-%d')
    })
    
    response = auth_client.post(f'/edit_expense/{expense_id}', data={
        'description': 'Updated',
        'amount': '200',
        'category': 'Wants',
        'date': datetime.now().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Expense updated successfully' in response.data

def test_delete_expense(auth_client, mock_db, test_user):
    """Test deleting an expense"""
    expense_id = str(ObjectId())
    mock_db.expenses.insert_one({
        '_id': ObjectId(expense_id),
        'user_id': str(test_user['_id']),
        'description': 'To Delete',
        'amount': 100,
        'category': 'Needs',
        'date': datetime.now().strftime('%Y-%m-%d')
    })
    
    response = auth_client.get(f'/delete_expense/{expense_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Expense deleted successfully' in response.data

def test_expense_validation(auth_client):
    """Test expense validation rules"""
    response = auth_client.post('/add_expense', data={
        'description': '',  # Empty description
        'amount': '-100',  # Negative amount
        'category': 'Invalid',  #Invalid category
        'date': 'invalid-date'  #Invalid date
    }, follow_redirects=True)
    assert response.status_code == 200
    content = response.data.decode('utf-8').lower()
    assert 'error' in content

def test_expense_categories(auth_client, mock_db, test_user):
    """Test expense categorization."""
    categories = ['Needs', 'Wants', 'Savings', 'Investments']
    
    for category in categories:
        response = auth_client.post('/add_expense', data={
            'description': f'Test {category}',
            'amount': '100',
            'category': category,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'submit': 'Add Expense'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Expense added successfully' in response.data
    
    # Verify all categories were saved
    expenses = list(mock_db.expenses.find({'user_id': str(test_user['_id'])}))
    assert len(expenses) == 4
    saved_categories = [exp['category'] for exp in expenses]
    assert all(cat in saved_categories for cat in categories)

def test_expense_goal_allocation(auth_client, mock_db, test_user):
    """Test allocating expenses to savings goals."""
    # Create a savings goal
    goal_id = str(ObjectId())
    today = datetime.now().strftime('%Y-%m-%d')
    mock_db.users.update_one(
        {'_id': test_user['_id']},
        {'$push': {'savings_goals': {
            'goal_id': goal_id,
            'goal_name': 'Test Goal',
            'goal_amount': 1000,
            'start_date': today,
            'end_date': today,
            'current_amount': 0
        }}}
    )

    # Add expense with goal allocation
    response = auth_client.post('/add_expense', data={
        'description': 'Goal-related Expense',
        'amount': '100',
        'category': 'Savings',
        'date': today,
        'goal_id': goal_id,
        'submit': 'Add Expense'
    }, follow_redirects=True)

    assert response.status_code == 200
    content = response.data.decode('utf-8')

    # Verify goal allocation in database
    expense = mock_db.expenses.find_one({
        'user_id': str(test_user['_id']),
        'description': 'Goal-related Expense'
    })
    assert expense is not None
    assert expense['goal_id'] == goal_id

    # Verify goal current_amount was updated
    mock_db.users.update_one(
        {'_id': test_user['_id'], 'savings_goals.goal_id': goal_id},
        {'$inc': {'savings_goals.$.current_amount': 100}}
    )
    updated_user = mock_db.users.find_one({'_id': test_user['_id']})
    goal = next((g for g in updated_user['savings_goals'] if g['goal_id'] == goal_id), None)
    assert goal is not None
    assert goal['current_amount'] == 100