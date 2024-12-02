from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, mongo, login_manager
from app.forms import LoginForm, RegistrationForm, ExpenseForm, CategoryForm, BudgetSettingsForm
from app.models import User
from bson.objectid import ObjectId
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict


@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database using the user ID."""
    return User(user_id)


@app.route("/")
@login_required
def index():
    """Render the index page with the user's expenses and total expenses."""
    # Retrieve all expenses for the current user from the database
    expenses = list(mongo.db.expenses.find({"user_id": current_user.get_id()}))
    categories = mongo.db.expenses.distinct("category")
    total_expenses = sum(expense["amount"] for expense in expenses)
    # Create an instance of the ExpenseForm for adding new expenses
    form = ExpenseForm()
    # Render the index template with the expenses, total, and categories
    return render_template(
        "index.html",
        form=form,
        expenses=expenses,
        total_expenses=total_expenses,
        categories=categories,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login and render the login page."""
    form = LoginForm()
    if form.validate_on_submit():
        # Check if the user exists in the database
        user = mongo.db.users.find_one({"email": form.email.data})
        # Verify the password
        if user and check_password_hash(user["password"], form.password.data):
            user_obj = User(str(user["_id"]))
            # Log the user in
            login_user(user_obj)
            return redirect(url_for("index"))
        flash("Invalid email or password")  # Flash an error message if login fails
    # Render the login template with the form
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration and render the registration page."""
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the email is already registered
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user is None:
            # Hash the password and store the new user in the database
            hash_pass = generate_password_hash(form.password.data)
            mongo.db.users.insert_one({"email": form.email.data, "password": hash_pass})
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Email already registered", "error")  # Flash an error if the email exists
    else:
        flash("Please correct the highlighted fields.", "error")  # Flash an error for form validation issues
    # Render the registration template with the form
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    """Log out the current user and redirect to the login page."""
    logout_user()  # Log the user out
    return redirect(url_for("login"))  # Redirect to the login page


@app.route("/add_expense", methods=["POST"])
@login_required
def add_expense():
    """Add a new expense to the database."""
    form = ExpenseForm()
    if form.validate_on_submit():
        # Insert the new expense into the database
        mongo.db.expenses.insert_one(
            {
                "user_id": current_user.get_id(),
                "description": form.description.data,
                "amount": float(form.amount.data),
                "category": form.category.data,
                "date": str(form.date.data),
            }
        )
        flash("Expense added successfully!")  # Flash a success message
    return redirect(url_for("index"))  # Redirect to the index page


@app.route("/edit_expense/<expense_id>", methods=["POST"])
@login_required
def edit_expense(expense_id):
    """Edit an existing expense in the database."""
    form = ExpenseForm()
    valid_categories = [choice[0] for choice in form.category.choices]

    # Prepare the updated expense data
    updated_expense = {
        "description": request.form["description"],
        "amount": float(request.form["amount"]),
        "category": request.form["category"],
        "date": request.form["date"],
    }
    # Update the expense in the database
    mongo.db.expenses.update_one(
        {"_id": ObjectId(expense_id), "user_id": current_user.get_id()},
        {"$set": updated_expense},
    )
    flash("Expense updated successfully!")  # Flash a success message
    return redirect(url_for("index"))  # Redirect to the index page


@app.route("/delete_expense/<expense_id>")
@login_required
def delete_expense(expense_id):
    """Delete an expense from the database."""
    # Remove the expense from the database
    mongo.db.expenses.delete_one(
        {"_id": ObjectId(expense_id), "user_id": current_user.get_id()}
    )
    flash("Expense deleted successfully!")  # Flash a success message
    return redirect(url_for("index"))  # Redirect to the index page


@app.route("/summary")
@login_required
def summary():
    """Render the summary page with financial analytics."""
    # Retrieve all expenses for the current user from the database
    expenses = list(mongo.db.expenses.find({"user_id": current_user.get_id()}))
    total_expenses = sum(e['amount'] for e in expenses)  # Calculate total expenses
    
    # Fetch user-defined budget settings
    user_settings = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    budget_settings = user_settings.get("budget_settings", {"needs": 50, "wants": 30, "savings": 20})

    # Define the date range for the summary (last 12 months)
    end_date = datetime.now()
    start_date = end_date - relativedelta(months=11)
    
    # Filter recent expenses within the last 12 months
    recent_expenses = [
        expense for expense in expenses 
        if datetime.strptime(expense['date'], '%Y-%m-%d') >= start_date
    ]
    # Calculate the monthly average of recent expenses
    monthly_average = sum(e['amount'] for e in recent_expenses) / 12

    # Initialize a dictionary to hold monthly totals
    monthly_totals = {}
    current_date = start_date
    # Populate the monthly_totals dictionary with keys for each month
    while current_date <= end_date:
        month_key = current_date.strftime('%Y-%m')
        monthly_totals[month_key] = 0.0  # Initialize each month's total to 0.0
        current_date += relativedelta(months=1)
    
    # Calculate total expenses for each month
    for expense in expenses:
        date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
        if start_date <= date_obj <= end_date:  # Check if the expense is within the date range
            month_key = date_obj.strftime('%Y-%m')
            monthly_totals[month_key] += expense['amount']  # Accumulate the amount for the month
    
    sorted_months = sorted(monthly_totals.keys())  # Sort the months for display
    
    # Prepare time data for rendering in the template
    time_data = {
        "labels": [datetime.strptime(m, '%Y-%m').strftime('%B %Y') for m in sorted_months],
        "values": [monthly_totals[m] for m in sorted_months]
    }
    
    # Organize expenses by category for further analysis
    expenses_by_category = defaultdict(list)
    
    for expense in expenses:
        date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
        category = expense['category']
        amount = expense['amount']
        expenses_by_category[category].append({
            'date': date_obj.strftime('%Y-%m-%d'),
            'amount': amount
        })
    
    # Prepare category data for rendering in the template
    category_data = {
        "labels": [],
        "values": [],
        "dates": [],
        "monthly_data": {}  
    }
    
    # Calculate totals for each category
    for category, expense_list in expenses_by_category.items():
        monthly_totals = defaultdict(float)  # Initialize monthly totals for the category
        for expense in expense_list:
            date = datetime.strptime(expense['date'], '%Y-%m-%d')
            month_key = date.strftime('%Y-%m')
            monthly_totals[month_key] += expense['amount']  # Accumulate the amount for the month
        
        # Append category data for rendering
        category_data["labels"].append(category)
        category_data["values"].append(sum(expense['amount'] for expense in expense_list))
        category_data["dates"].extend([expense['date'] for expense in expense_list])
        category_data["monthly_data"][category] = dict(monthly_totals)

    # Render the summary template with the calculated data
    return render_template(
        "summary.html",
        total_expenses=total_expenses,
        monthly_average=monthly_average,
        time_data=time_data,
        category_data=category_data,
        budget_settings=budget_settings
    )


@app.route("/budget_settings", methods=["GET", "POST"])
@login_required
def budget_settings():
    form = BudgetSettingsForm()
    if form.validate_on_submit():
        # Calculate wants percentage
        wants_percentage = 100 - (form.needs_percentage.data + form.savings_percentage.data)
        
        # Ensure the total does not exceed 100%
        if wants_percentage < 0:
            flash("The total percentages cannot exceed 100%. Please adjust your inputs.", "error")
            return redirect(url_for("budget_settings"))

        # Save the settings to the database
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {
                "budget_settings": {
                    "needs": form.needs_percentage.data,
                    "wants": wants_percentage,
                    "savings": form.savings_percentage.data
                }
            }}
        )
        flash("Budget settings updated successfully!", "success")
        return redirect(url_for("index"))
    
    # Load current settings if they exist
    user_settings = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    if user_settings and "budget_settings" in user_settings:
        form.needs_percentage.data = user_settings["budget_settings"]["needs"]
        form.savings_percentage.data = user_settings["budget_settings"]["savings"]

    return render_template("budget_settings.html", form=form)
