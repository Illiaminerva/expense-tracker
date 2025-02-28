from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, mongo, login_manager
from app.forms import LoginForm, RegistrationForm, ExpenseForm, BudgetSettingsForm
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
            user_id = mongo.db.users.insert_one({"email": form.email.data, "password": hash_pass}).inserted_id
            
            # Log the user in
            user_obj = User(str(user_id))
            login_user(user_obj)

            flash("Registration successful! Please complete your onboarding.", "success")
            return redirect(url_for("onboarding_step1"))  # Redirect to the onboarding page
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
        budget_needs = round(form.needs_percentage.data, 2)
        budget_savings = round(form.savings_percentage.data, 2)
        budget_investments = round(form.investments_percentage.data, 2)
        budget_wants = round(form.wants_percentage.data, 2)

        # Ensure the total does not exceed 100%
        total_percentage = budget_needs + budget_savings + budget_investments + budget_wants
        if total_percentage > 100:
            flash("The total percentages cannot exceed 100%. Please adjust your inputs.", "error")
            return redirect(url_for("budget_settings"))

        # Save budget settings to the user's settings in the database
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {
                "budget_settings": {
                    "needs": budget_needs,
                    "savings": budget_savings,
                    "investments": budget_investments,
                    "wants": budget_wants
                }
            }}
        )
        flash("Budget settings updated successfully!", "success")
        return redirect(url_for("index"))

    # Load current settings if they exist
    user_settings = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    if user_settings and "budget_settings" in user_settings:
        form.needs_percentage.data = round(user_settings["budget_settings"]["needs"], 2)
        form.wants_percentage.data = round(user_settings["budget_settings"].get("wants", 0), 2)
        form.savings_percentage.data = round(user_settings["budget_settings"]["savings"], 2)
        form.investments_percentage.data = round(user_settings["budget_settings"].get("investments", 0), 2)

    return render_template("budget_settings.html", form=form)


@app.route("/set_savings_goal", methods=["GET", "POST"])
@login_required
def set_savings_goal():
    """Render the savings goal form and handle submissions."""
    user_settings = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})

    # Retrieve savings goal
    savings_goal = user_settings.get("savings_goal", {"goal_amount": 0, "start_date": "", "end_date": ""})

    # Initialize total savings and savings data
    total_savings = 0
    savings_data = {
        "dates": [],
        "cumulative_amounts": []
    }

    if request.method == "POST":
        # Handle setting a new savings goal
        goal_name = request.form.get("goal_name", "")
        goal_amount = float(request.form.get("goal_amount", 0))
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")

        # Update the savings goal in the database
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {
                "savings_goal": {
                    "goal_name": goal_name,
                    "goal_amount": goal_amount,
                    "start_date": start_date,
                    "end_date": end_date
                }
            }}
        )
        flash("Savings goal set successfully!", "success")
        return redirect(url_for("set_savings_goal"))

    # Calculate total savings from expenses in the "savings" category within the date range
    expenses = list(mongo.db.expenses.find({"user_id": str(current_user.get_id()), "category": "savings"}))

    # Filter expenses within the savings goal date range and sort by date
    if savings_goal['start_date'] and savings_goal['end_date']:
        start_date_obj = datetime.strptime(savings_goal['start_date'], '%Y-%m-%d')
        end_date_obj = datetime.strptime(savings_goal['end_date'], '%Y-%m-%d')
        filtered_expenses = [expense for expense in expenses if start_date_obj <= datetime.strptime(expense['date'], '%Y-%m-%d') <= end_date_obj]
    else:
        filtered_expenses = expenses

    # Sort expenses by date
    filtered_expenses.sort(key=lambda x: x['date'])

    # Prepare savings data for the chart
    cumulative_amount = 0
    for expense in filtered_expenses:
        expense_date = expense['date']
        amount = expense['amount']
        cumulative_amount += amount
        savings_data['dates'].append(expense_date)
        savings_data['cumulative_amounts'].append(cumulative_amount)

    total_savings = cumulative_amount

    # Calculate progress towards the savings goal
    progress = (total_savings / savings_goal['goal_amount'] * 100) if savings_goal['goal_amount'] > 0 else 0

    return render_template("set_savings_goal.html", savings_goal=savings_goal, progress=progress, savings_data=savings_data, total_savings=total_savings)


@app.route("/onboarding/step1", methods=["GET", "POST"])
@login_required
def onboarding_step1():
    """Handle budget settings during onboarding."""
    form = BudgetSettingsForm()

    if form.validate_on_submit():
        # Round input values to avoid floating-point errors
        budget_needs = round(form.needs_percentage.data, 2)
        budget_wants = round(form.wants_percentage.data, 2)
        budget_savings = round(form.savings_percentage.data, 2)

        # Calculate investments automatically
        budget_investments = round(100 - (budget_needs + budget_wants + budget_savings), 2)

        # Ensure total does not exceed 100%
        if budget_investments < 0:
            flash("The total percentages cannot exceed 100%. Please adjust your inputs.", "error")
            return redirect(url_for("onboarding_step1"))

        # Save budget settings to the user's database entry
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {
                "budget_settings": {
                    "needs": budget_needs,
                    "wants": budget_wants,
                    "savings": budget_savings,
                    "investments": budget_investments
                }
            }}
        )

        flash("Budget settings saved successfully!", "success")
        return redirect(url_for("onboarding_step2"))

    return render_template("onboarding_step1.html", form=form)

@app.route("/onboarding/step2", methods=["GET", "POST"])
@login_required
def onboarding_step2():
    form = ExpenseForm()
    if request.method == "POST":
        if form.validate_on_submit():  # Validate form submission
            first_expense = {
            "description": form.description.data,
            "amount": float(form.amount.data),
            "category": form.category.data,
            "user_id": current_user.get_id(),
            "date": form.date.data.strftime('%Y-%m-%d') 
        }

        mongo.db.expenses.insert_one(first_expense)
        return redirect(url_for("onboarding_step3"))

    return render_template("onboarding_step2.html", form=form)  # Render step 2 template


@app.route("/onboarding/step3", methods=["GET", "POST"])
@login_required
def onboarding_step3():
    if request.method == "POST":
        # Handle setting a new savings goal
        goal_name = request.form.get("goal_name", "")
        goal_amount = float(request.form.get("goal_amount", 0))
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")

        # Update the savings goal in the database
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {
                "savings_goal": {
                    "goal_name": goal_name,
                    "goal_amount": goal_amount,
                    "start_date": start_date,
                    "end_date": end_date
                }
            }}
        )

        flash("Onboarding completed successfully!", "success")
        return redirect(url_for("index"))  # Redirect to the main dashboard

    return render_template("onboarding_step3.html")  # Render step 3 template