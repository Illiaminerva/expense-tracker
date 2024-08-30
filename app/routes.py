from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, mongo, login_manager  # Import login_manager from __init__.py
from app.forms import LoginForm, RegistrationForm, ExpenseForm, CategoryForm
from app.models import User
from bson.objectid import ObjectId

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@login_required
def index():
    expenses = list(mongo.db.expenses.find({'user_id': current_user.get_id()}))
    categories = mongo.db.expenses.distinct('category')
    total_expenses = sum(expense['amount'] for expense in expenses)
    form = ExpenseForm()
    return render_template('index.html', form=form, expenses=expenses, total_expenses=total_expenses, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'email': form.email.data})
        if user and check_password_hash(user['password'], form.password.data):
            user_obj = User(str(user['_id']))
            login_user(user_obj)
            return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one({'email': form.email.data})
        if existing_user is None:
            hash_pass = generate_password_hash(form.password.data)
            mongo.db.users.insert_one({'email': form.email.data, 'password': hash_pass})
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))
        flash('Email already registered')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        category = request.form.get('category')
        if category == 'new':
            category = request.form.get('new_category')
        
        expense = {
            'user_id': current_user.get_id(),
            'description': form.description.data,
            'amount': float(form.amount.data),
            'category': category,
            'date': form.date.data.strftime('%Y-%m-%d')  # Ensure date is stored as a string
        }
        mongo.db.expenses.insert_one(expense)
        flash('Expense added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_category/<category_id>')
@login_required
def delete_category(category_id):
    mongo.db.categories.delete_one({'_id': ObjectId(category_id), 'user_id': current_user.get_id()})
    flash('Category deleted successfully!')
    return redirect(url_for('categories'))

@app.route('/edit_expense/<expense_id>', methods=['POST'])
@login_required
def edit_expense(expense_id):
    updated_expense = {
        'description': request.form['description'],
        'amount': float(request.form['amount']),
        'category': request.form['category'],
        'date': request.form['date']
    }
    mongo.db.expenses.update_one(
        {'_id': ObjectId(expense_id), 'user_id': current_user.get_id()},
        {'$set': updated_expense}
    )
    flash('Expense updated successfully!')
    return redirect(url_for('index'))

@app.route('/delete_expense/<expense_id>')
@login_required
def delete_expense(expense_id):
    mongo.db.expenses.delete_one({'_id': ObjectId(expense_id), 'user_id': current_user.get_id()})
    flash('Expense deleted successfully!')
    return redirect(url_for('index'))

from collections import defaultdict
from flask import render_template
from flask_login import login_required, current_user
from app import app, mongo
from datetime import datetime

@app.route('/summary')
@login_required
def summary():
    expenses = list(mongo.db.expenses.find({'user_id': current_user.get_id()}))
    # Check if expenses exist
    if not expenses:
        flash('No expenses to show in the summary.')
        return render_template('summary.html', category_data={}, time_data={})

    # Prepare data for "Expenses by Category" chart
    category_totals = defaultdict(float)
    for expense in expenses:
        category_totals[expense['category']] += expense['amount']

    category_data = {
        'labels': list(category_totals.keys()),
        'values': list(category_totals.values())
    }

    # Prepare data for "Expenses Over Time" chart
    expenses_by_date = defaultdict(float)
    for expense in expenses:
        date_str = datetime.strptime(expense['date'], '%Y-%m-%d').strftime('%Y-%m-%d')
        expenses_by_date[date_str] += expense['amount']

    sorted_dates = sorted(expenses_by_date.keys())
    time_data = {
        'labels': sorted_dates,
        'values': [expenses_by_date[date] for date in sorted_dates]
    }

    return render_template('summary.html', category_data=category_data, time_data=time_data)

