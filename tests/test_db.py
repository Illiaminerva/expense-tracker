import pytest
from datetime import datetime, timedelta
import unittest.mock as mock
from bson import ObjectId
from werkzeug.security import generate_password_hash

def test_get_user_by_email(mock_db):
    """Test retrieving a user by email."""
    # Create test user
    user_data = {
        "email": "test@example.com",
        "password": generate_password_hash("password123"),
        "created_at": datetime.now()
    }
    mock_db.users.insert_one(user_data)
    
    # Test retrieval
    user = mock_db.users.find_one({"email": "test@example.com"})
    assert user is not None
    assert user["email"] == "test@example.com"

def test_create_user(mock_db):
    """Test creating a new user."""
    user_data = {
        "email": "newuser@example.com",
        "password": generate_password_hash("password123"),
        "created_at": datetime.now(),
        "budget_settings": {
            "needs": 50,
            "wants": 30,
            "savings": 10,
            "investments": 10
        }
    }
    
    result = mock_db.users.insert_one(user_data)
    assert result.inserted_id is not None
    
    user = mock_db.users.find_one({"_id": result.inserted_id})
    assert user is not None
    assert user["email"] == "newuser@example.com"
    assert user["budget_settings"]["investments"] == 10

def test_get_user_expenses(mock_db):
    """Test retrieving user expenses."""
    # Create test user
    user_id = ObjectId()
    
    # Add test expenses
    expenses = [
        {
            "user_id": str(user_id),
            "description": "Expense 1",
            "amount": 100.00,
            "category": "Needs",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "user_id": str(user_id),
            "description": "Expense 2",
            "amount": 50.00,
            "category": "Wants",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "user_id": str(user_id),
            "description": "Expense 3",
            "amount": 75.00,
            "category": "Investments",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    ]
    
    mock_db.expenses.insert_many(expenses)
    
    # Test retrieval
    user_expenses = list(mock_db.expenses.find({"user_id": str(user_id)}))
    assert len(user_expenses) == 3
    assert sum(expense["amount"] for expense in user_expenses) == 225.00
    
    # Test category filtering
    investment_expenses = list(mock_db.expenses.find({
        "user_id": str(user_id),
        "category": "Investments"
    }))
    assert len(investment_expenses) == 1
    assert investment_expenses[0]["amount"] == 75.00

def test_add_expense(mock_db):
    """Test adding a new expense."""
    user_id = ObjectId()
    expense_data = {
        "user_id": str(user_id),
        "description": "Investment Purchase",
        "amount": 75.00,
        "category": "Investments",
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    result = mock_db.expenses.insert_one(expense_data)
    assert result.inserted_id is not None
    
    expense = mock_db.expenses.find_one({"_id": result.inserted_id})
    assert expense is not None
    assert expense["amount"] == 75.00
    assert expense["category"] == "Investments"

def test_get_user_settings(mock_db):
    """Test retrieving user settings."""
    user_id = ObjectId()
    user_data = {
        "_id": user_id,
        "email": "test@example.com",
        "budget_settings": {
            "needs": 50,
            "wants": 20,
            "savings": 20,
            "investments": 10
        }
    }
    
    mock_db.users.insert_one(user_data)
    
    user = mock_db.users.find_one({"_id": user_id})
    assert user is not None
    assert user["budget_settings"]["needs"] == 50
    assert user["budget_settings"]["wants"] == 20
    assert user["budget_settings"]["savings"] == 20
    assert user["budget_settings"]["investments"] == 10
    assert sum(user["budget_settings"].values()) == 100

def test_update_user_settings(mock_db):
    """Test updating user settings."""
    user_id = ObjectId()
    user_data = {
        "_id": user_id,
        "email": "test@example.com",
        "budget_settings": {
            "needs": 50,
            "wants": 30,
            "savings": 10,
            "investments": 10
        }
    }
    
    mock_db.users.insert_one(user_data)
    
    # Update settings
    new_settings = {
        "needs": 40,
        "wants": 30,
        "savings": 15,
        "investments": 15
    }
    
    mock_db.users.update_one(
        {"_id": user_id},
        {"$set": {"budget_settings": new_settings}}
    )
    
    user = mock_db.users.find_one({"_id": user_id})
    assert user["budget_settings"]["needs"] == 40
    assert user["budget_settings"]["wants"] == 30
    assert user["budget_settings"]["savings"] == 15
    assert user["budget_settings"]["investments"] == 15
    assert sum(user["budget_settings"].values()) == 100

def test_update_user(mock_db):
    """Test updating user information."""
    user_id = ObjectId()
    user_data = {
        "_id": user_id,
        "email": "test@example.com",
        "password": generate_password_hash("oldpassword"),
        "budget_settings": {
            "needs": 50,
            "wants": 20,
            "savings": 15,
            "investments": 15
        }
    }
    
    mock_db.users.insert_one(user_data)
    
    # Update user
    new_password = generate_password_hash("newpassword")
    new_settings = {
        "needs": 45,
        "wants": 25,
        "savings": 15,
        "investments": 15
    }
    
    mock_db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "password": new_password,
                "budget_settings": new_settings
            }
        }
    )
    
    user = mock_db.users.find_one({"_id": user_id})
    assert user["password"] == new_password
    assert user["budget_settings"]["investments"] == 15
    assert sum(user["budget_settings"].values()) == 100