from datetime import datetime, timedelta
from bson import ObjectId

# Test if the index page requires a user to be logged in
def test_index_requires_login(client):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Should redirect to login page

# Test if the login page renders correctly
def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

# Test if the register page renders correctly
def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

# Test successful login with valid credentials
def test_successful_login(client, test_user):
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Expense Tracker' in response.data # Make sure Expense Tracker name is on the page

# Test failed login with incorrect password
def test_failed_login(client):
    response = client.post('/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data  # Make sure the error is showing

# Test logout functionality
def test_logout(auth_client):
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Should redirect back to login page

# Test adding an expense while logged in
def test_add_expense(auth_client, mongo, test_user):
    response = auth_client.get('/')
    assert response.status_code == 200
    assert b'Login' not in response.data
    assert b'Logout' in response.data

    # Adding an expense
    response = auth_client.post('/add_expense', data={
        'user_id': str(test_user['_id']),
        "description": "Test Expense",
        "amount": "100.00",
        "category": "needs",
        "date": datetime.now().strftime("%Y-%m-%d"),
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Expense added successfully!' in response.data # Making sure the alert shows up

    # Verify the expense exists in the database
    expense = mongo.db.expenses.find_one({"description": "Test Expense"})
    assert expense is not None
    assert expense['description'] == 'Test Expense'
    assert expense['amount'] == 100.00
    assert expense['category'] == 'needs'

# Test editing an expense
def test_edit_expense(auth_client, mongo, test_user):
    # Add an expense to edit
    expense_id = mongo.db.expenses.insert_one({
        'user_id': str(test_user['_id']),
        'description': 'Expense to Edit',
        'amount': 50.00,
        'category': 'wants',
        'date': datetime.now().strftime('%Y-%m-%d')
    }).inserted_id

    # Edit the expense
    response = auth_client.post(f'/edit_expense/{expense_id}', data={
        'description': 'Edited Expense',
        'amount': '75.00',
        'category': 'needs',
        'date': datetime.now().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Expense updated successfully' in response.data

    # Verify the expense was updated as expected
    updated_expense = mongo.db.expenses.find_one({'_id': expense_id})
    assert updated_expense['description'] == 'Edited Expense'
    assert updated_expense['amount'] == 75.00

# Test deleting an expense
def test_delete_expense(auth_client, mongo, test_user):
    # Add an expense to delete
    expense_id = mongo.db.expenses.insert_one({
        'user_id': str(test_user['_id']),
        'description': 'Expense to Delete',
        'amount': 25.00,
        'category': 'wants',
        'date': datetime.now().strftime('%Y-%m-%d')
    }).inserted_id

    # Delete the expense
    response = auth_client.get(f'/delete_expense/{expense_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'Expense deleted successfully' in response.data

    # Verify that this expense doesn't exist anymore
    deleted_expense = mongo.db.expenses.find_one({'_id': expense_id})
    assert deleted_expense is None

# Test the summary page displays correct totals
def test_summary_page(auth_client, mongo, test_user):
    # Add some test expenses
    today = datetime.now()
    mongo.db.expenses.insert_many([
        {
            'user_id': str(test_user['_id']),
            'description': 'Expense 1',
            'amount': 100.00,
            'category': 'needs',
            'date': today.strftime('%Y-%m-%d')
        },
        {
            'user_id': str(test_user['_id']),
            'description': 'Expense 2',
            'amount': 200.00,
            'category': 'wants',
            'date': (today - timedelta(days=30)).strftime('%Y-%m-%d')
        }
    ])

    # Fetch the summary page
    response = auth_client.get('/summary')
    assert response.status_code == 200

    # Verify the statistics are as expected 
    content = response.data
    assert b'Total Spending' in content
    assert b'300.00' in content  
    assert b'Average Monthly' in content  