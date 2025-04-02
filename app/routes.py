from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, mongo, login_manager
from app.forms import LoginForm, RegistrationForm, ExpenseForm, BudgetSettingsForm
from app.models import User
from bson.objectid import ObjectId
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import random


# List of financial facts to display to users
FINANCIAL_FACTS = [
    "Setting specific savings goals increases your chance of saving successfully by 42%.",
    "People who track their expenses regularly save up to 20% more money than those who don't.",
    "Automating your savings can increase your annual savings rate by up to 56%.",
    "Following the 50/30/20 budget rule (needs/wants/savings) can help you build emergency savings 3x faster.",
    "Individuals with written financial goals are 33% more likely to achieve them.",
    "Reducing impulse purchases can save the average person over $5,000 per year.",
    "People who check their financial progress weekly are 30% more likely to reach their financial goals.",
    "Having an emergency fund reduces financial stress by up to 60%.",
    "Saving just 1% more of your income can add over $50,000 to your retirement over 30 years.",
    "Paying yourself first (saving before spending) can increase your savings rate by 25%.",
    "People who categorize their expenses save on average 15% more than those who don't.",
    "Setting up automatic transfers to savings accounts increases the likelihood of maintaining a savings habit by 70%.",
    "Individuals who review their budget monthly are 80% more likely to stay on track with financial goals.",
    "Visualizing your savings goals makes you 58% more likely to achieve them.",
    "People who share their financial goals with others have a 65% higher success rate.",
    "Using cash instead of credit cards for discretionary spending can reduce your expenses by up to 23%.",
    "Saving 15% of your income throughout your career could allow you to maintain your lifestyle in retirement.",
    "Tracking your net worth regularly increases your wealth accumulation by an average of 15% over 10 years.",
    "People who invest regularly outperform those who try to time the market by an average of 3% annually.",
    "Having multiple savings goals (short, medium, and long-term) increases overall financial success by 40%."
]


def get_random_fact():
    """Return a random financial fact from the list."""
    return random.choice(FINANCIAL_FACTS)


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
    
    # Get user's savings goals for the dropdown
    user_settings = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    
    # Initialize goals as an empty list if user_settings is None
    goals = []
    if user_settings:
        goals = user_settings.get("savings_goals", [])
    
    # Create an instance of the ExpenseForm for adding new expenses
    form = ExpenseForm()
    
    # Get a random financial fact
    financial_fact = get_random_fact()
    
    # Render the index template with the expenses, total, and categories
    return render_template(
        "index.html",
        form=form,
        expenses=expenses,
        total_expenses=total_expenses,
        categories=categories,
        goals=goals,
        financial_fact=financial_fact
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
    """Register a new user."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for("login"))
        
        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        # Create ObjectId first, then convert to string
        obj_id = ObjectId()
        user_id = str(obj_id)
        mongo.db.users.insert_one({
            "_id": obj_id,
            "email": form.email.data,
            "password": hashed_password,
            "onboarding_complete": False,
            "created_at": datetime.now()
        })
        
        # Log in the new user
        user = User(user_id)
        login_user(user)
        
        flash("Account created successfully! Let's set up your profile.", "success")
        return redirect(url_for("onboarding"))
    
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
        # Get the goal_id if provided
        goal_id = request.form.get("goal_id", "")
        
        # Prepare expense data
        expense_data = {
            "user_id": current_user.get_id(),
            "description": form.description.data,
            "amount": float(form.amount.data),
            "category": form.category.data,
            "date": str(form.date.data),
        }
        
        # Add goal_id if provided and category is Savings or Investments
        if goal_id and form.category.data in ["Savings", "Investments"]:
            # Get the goal details
            user_settings = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
            if user_settings and "savings_goals" in user_settings:
                goal = next((g for g in user_settings["savings_goals"] if g["goal_id"] == goal_id), None)
                if goal:
                    # Check if expense date is within goal date range
                    expense_date = datetime.strptime(str(form.date.data), '%Y-%m-%d')
                    goal_start = datetime.strptime(goal["start_date"], '%Y-%m-%d')
                    goal_end = datetime.strptime(goal["end_date"], '%Y-%m-%d')
                    
                    if goal_start <= expense_date <= goal_end:
                        expense_data["goal_id"] = goal_id
                    else:
                        error_msg = f"Expense date must be between {goal['start_date']} and {goal['end_date']} for this goal"
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return jsonify({
                                "success": False, 
                                "message": error_msg
                            }), 400  # Return 400 Bad Request status
                        flash(error_msg, "error")
                        return redirect(url_for("index"))
        
        # Insert the new expense into the database
        mongo.db.expenses.insert_one(expense_data)
        
        # Check if this is from onboarding
        from_onboarding = request.form.get("from_onboarding") == "true"
        
        success_msg = "Expense added successfully!"
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": True, "message": success_msg})
        
        if from_onboarding:
            return redirect(url_for("onboarding", step=3))
        else:
            flash(success_msg, "success")
            return redirect(url_for("index"))
    
    # If form validation fails
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            "success": False,
            "message": "Please check your input and try again."
        }), 400
    return redirect(url_for("index"))


@app.route("/edit_expense/<expense_id>", methods=["POST"])
@login_required
def edit_expense(expense_id):
    """Edit an existing expense in the database."""
    form = ExpenseForm()
    valid_categories = [choice[0] for choice in form.category.choices]

    # Get the goal_id if provided
    goal_id = request.form.get("goal_id", "")
    
    # Prepare the updated expense data
    updated_expense = {
        "description": request.form["description"],
        "amount": float(request.form["amount"]),
        "category": request.form["category"],
        "date": request.form["date"],
    }
    
    # Add goal_id if provided and category is Savings or Investments
    if goal_id and request.form["category"] in ["Savings", "Investments"]:
        # Get the goal details
        user_settings = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
        if user_settings and "savings_goals" in user_settings:
            goal = next((g for g in user_settings["savings_goals"] if g["goal_id"] == goal_id), None)
            if goal:
                # Check if expense date is within goal date range
                expense_date = datetime.strptime(updated_expense["date"], '%Y-%m-%d')
                goal_start = datetime.strptime(goal["start_date"], '%Y-%m-%d')
                goal_end = datetime.strptime(goal["end_date"], '%Y-%m-%d')
                
                if goal_start <= expense_date <= goal_end:
                    updated_expense["goal_id"] = goal_id
                else:
                    error_msg = f"Expense date must be between {goal['start_date']} and {goal['end_date']} for this goal"
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            "success": False,
                            "message": error_msg
                        }), 400
                    flash(error_msg, "error")
                    return redirect(url_for("index"))
    
    # Update the expense in the database
    if "goal_id" in updated_expense:
        # If goal_id is valid and date is within range, update with new goal_id
        mongo.db.expenses.update_one(
            {"_id": ObjectId(expense_id), "user_id": current_user.get_id()},
            {"$set": updated_expense}
        )
    else:
        # If no valid goal_id, remove goal_id if it exists
        mongo.db.expenses.update_one(
            {"_id": ObjectId(expense_id), "user_id": current_user.get_id()},
            {
                "$set": updated_expense,
                "$unset": {"goal_id": ""}
            }
        )
    
    success_msg = "Expense updated successfully!"
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "message": success_msg})
    flash(success_msg, "success")
    return redirect(url_for("index"))


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
    
    # Handle case when user_settings is None
    if user_settings is None:
        budget_settings = {"needs": 50, "wants": 20, "savings": 20, "investments": 10}
    else:
        budget_settings = user_settings.get("budget_settings", {"needs": 50, "wants": 20, "savings": 20, "investments": 10})

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

    # Get a random financial fact
    financial_fact = get_random_fact()
    
    # Render the summary template with the calculated data
    return render_template(
        "summary.html",
        total_expenses=total_expenses,
        monthly_average=monthly_average,
        time_data=time_data,
        category_data=category_data,
        budget_settings=budget_settings,
        financial_fact=financial_fact
    )


@app.route("/budget_settings", methods=["GET", "POST"])
@login_required
def budget_settings():
    """Handle budget allocation settings and display the budget settings form."""
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
            }},
            upsert=True  # Create the document if it doesn't exist
        )
        flash("Budget settings updated successfully!", "success")
        return redirect(url_for("index"))

    # Load current settings if they exist
    user_settings = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
    
    # Set default values if user_settings is None or budget_settings is not present
    if user_settings is None or "budget_settings" not in user_settings:
        form.needs_percentage.data = 50
        form.wants_percentage.data = 30
        form.savings_percentage.data = 10
        form.investments_percentage.data = 10
    else:
        form.needs_percentage.data = round(user_settings["budget_settings"].get("needs", 0), 2)
        form.wants_percentage.data = round(user_settings["budget_settings"].get("wants", 0), 2)
        form.savings_percentage.data = round(user_settings["budget_settings"].get("savings", 0), 2)
        form.investments_percentage.data = round(user_settings["budget_settings"].get("investments", 0), 2)

    # Get a random financial fact
    financial_fact = get_random_fact()
    
    return render_template("budget_settings.html", form=form, financial_fact=financial_fact)


@app.route("/set_savings_goal", methods=["GET", "POST"])
@login_required
def set_savings_goal():
    """Render the savings goals page and handle submissions."""
    user_settings = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})

    # Initialize savings_goals as an empty list if user_settings is None
    if user_settings is None:
        savings_goals = []
        # Create a default user settings document
        mongo.db.users.insert_one({
            "_id": ObjectId(current_user.get_id()),
            "savings_goals": [],
            "created_at": datetime.now()
        })
    else:
        # Retrieve savings goals
        savings_goals = user_settings.get("savings_goals", [])

    # Initialize goals data for the template
    goals_data = []
    
    # Process form submission for adding/editing a goal
    if request.method == "POST":
        action = request.form.get("action", "")
        
        if action == "add_goal" or action == "edit_goal":
            goal_id = request.form.get("goal_id", "")
            goal_name = request.form.get("goal_name", "")
            goal_amount = float(request.form.get("goal_amount", 0))
            start_date = request.form.get("start_date", "")
            end_date = request.form.get("end_date", "")
            
            # Create new goal object
            new_goal = {
                "goal_id": goal_id if goal_id else str(ObjectId()),
                "goal_name": goal_name,
                "goal_amount": goal_amount,
                "start_date": start_date,
                "end_date": end_date,
                "created_at": datetime.now().strftime('%Y-%m-%d')
            }
            
            # If editing, remove old goal first and update expenses
            if action == "edit_goal" and goal_id:
                old_goal = next((g for g in savings_goals if g.get("goal_id") == goal_id), None)
                if old_goal:
                    # Check if date range changed
                    if (old_goal["start_date"] != start_date or old_goal["end_date"] != end_date):
                        # Remove goal_id from expenses that are now outside the date range
                        new_start = datetime.strptime(start_date, '%Y-%m-%d')
                        new_end = datetime.strptime(end_date, '%Y-%m-%d')
                        
                        # Update all expenses with this goal_id
                        expenses = mongo.db.expenses.find({"user_id": current_user.get_id(), "goal_id": goal_id})
                        for expense in expenses:
                            expense_date = datetime.strptime(expense["date"], '%Y-%m-%d')
                            if not (new_start <= expense_date <= new_end):
                                # Remove goal_id if expense is outside new date range
                                mongo.db.expenses.update_one(
                                    {"_id": expense["_id"]},
                                    {"$unset": {"goal_id": ""}}
                                )
                
                savings_goals = [g for g in savings_goals if g.get("goal_id") != goal_id]
            
            # Add the new/updated goal
            savings_goals.append(new_goal)
            
            # Update the savings goals in the database
            mongo.db.users.update_one(
                {"_id": ObjectId(current_user.get_id())},
                {"$set": {"savings_goals": savings_goals}}
            )
            
            flash("Savings goal saved successfully!", "success")
            return redirect(url_for("set_savings_goal"))
            
        elif action == "delete_goal":
            goal_id = request.form.get("goal_id", "")
            if goal_id:
                # Remove goal_id from all expenses associated with this goal
                mongo.db.expenses.update_many(
                    {"user_id": current_user.get_id(), "goal_id": goal_id},
                    {"$unset": {"goal_id": ""}}
                )
                
                # Remove the goal with the specified ID
                savings_goals = [goal for goal in savings_goals if goal.get("goal_id") != goal_id]
                
                # Update the database
                mongo.db.users.update_one(
                    {"_id": ObjectId(current_user.get_id())},
                    {"$set": {"savings_goals": savings_goals}}
                )
                
                flash("Goal deleted successfully!", "success")
                return redirect(url_for("set_savings_goal"))

    # Process each goal to calculate progress
    for goal in savings_goals:
        goal_id = goal.get("goal_id", "")
        goal_amount = goal.get("goal_amount", 0)
        start_date = goal.get("start_date", "")
        end_date = goal.get("end_date", "")
        
        # Get all expenses allocated to this specific goal
        goal_expenses = list(mongo.db.expenses.find({
            "user_id": str(current_user.get_id()), 
            "category": {"$in": ["Savings", "Investments"]},
            "goal_id": goal_id  # Only get expenses explicitly allocated to this goal
        }).sort("date", 1))  # Sort by date ascending
        
        # Filter expenses within the goal date range
        if start_date and end_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            goal_expenses = [expense for expense in goal_expenses if 
                           start_date_obj <= datetime.strptime(expense['date'], '%Y-%m-%d') <= end_date_obj]

        # Prepare savings data for the chart
        savings_data = {
            "dates": [],
            "cumulative_amounts": []
        }
        
        # Calculate cumulative savings
        total_savings = 0
        for expense in goal_expenses:
            total_savings += expense['amount']
            savings_data['dates'].append(expense['date'])
            savings_data['cumulative_amounts'].append(total_savings)

        # Calculate progress towards the savings goal
        progress = (total_savings / goal_amount * 100) if goal_amount > 0 else 0
        
        # Add goal data for the template
        goals_data.append({
            "goal": goal,
            "progress": progress,
            "total_savings": total_savings,
            "savings_data": savings_data,
            "allocated_expenses": goal_expenses  # Pass the allocated expenses to the template
        })

    # Get a random financial fact
    financial_fact = get_random_fact()
    
    return render_template("set_savings_goal.html", goals_data=goals_data, financial_fact=financial_fact)


@app.route("/onboarding/step1", methods=["GET", "POST"])
@login_required
def onboarding_step1():
    """Handle budget settings during onboarding."""
    form = BudgetSettingsForm()

    if request.method == "POST":
        # Get values directly from form data
        needs_percentage = float(request.form.get("needs_percentage", 0))
        wants_percentage = float(request.form.get("wants_percentage", 0))
        savings_percentage = float(request.form.get("savings_percentage", 0))
        
        # Calculate investments automatically
        investments_percentage = 100 - needs_percentage - wants_percentage - savings_percentage
        
        # Ensure total does not exceed 100%
        if investments_percentage < 0:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "message": "The total percentages cannot exceed 100%. Please adjust your inputs."})
            flash("The total percentages cannot exceed 100%. Please adjust your inputs.", "error")
            return redirect(url_for("onboarding"))
        
        # Save budget settings to the user's database entry
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {
                "budget_settings": {
                    "needs": needs_percentage,
                    "wants": wants_percentage,
                    "savings": savings_percentage,
                    "investments": investments_percentage
                }
            }}
        )
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": True, "message": "Budget settings saved successfully!"})
        
        flash("Budget settings saved successfully!", "success")
        return redirect(url_for("onboarding_step2"))

    return render_template("onboarding_step1.html", form=form)

@app.route("/onboarding/step2", methods=["GET", "POST"])
@login_required
def onboarding_step2():
    form = ExpenseForm()
    if request.method == "POST":
        # Get values directly from form data
        description = request.form.get("description", "")
        amount = float(request.form.get("amount", 0))
        category = request.form.get("category", "")
        date_str = request.form.get("date", "")
        
        # Validate required fields
        if not description or amount <= 0 or not category or not date_str:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "message": "Please fill in all required fields."})
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("onboarding"))
        
        # Create expense object
        first_expense = {
            "description": description,
            "amount": amount,
            "category": category,
            "user_id": current_user.get_id(),
            "date": date_str
        }
        
        # Save to database
        mongo.db.expenses.insert_one(first_expense)
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": True, "message": "Expense added successfully!"})
        
        return redirect(url_for("onboarding_step3"))

    return render_template("onboarding_step2.html", form=form)


@app.route("/onboarding/step3", methods=["GET", "POST"])
@login_required
def onboarding_step3():
    if request.method == "POST":
        # Handle setting a new savings goal
        goal_name = request.form.get("goal_name", "")
        goal_amount = float(request.form.get("goal_amount", 0))
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")
        
        # Create a new goal with a unique ID
        new_goal = {
            "goal_id": str(ObjectId()),
            "goal_name": goal_name,
            "goal_amount": goal_amount,
            "start_date": start_date,
            "end_date": end_date,
            "created_at": datetime.now().strftime('%Y-%m-%d')
        }
        
        # Check if user document exists
        user_exists = mongo.db.users.find_one({"_id": ObjectId(current_user.get_id())})
        
        if user_exists:
            # Update the savings goals in the database
            mongo.db.users.update_one(
                {"_id": ObjectId(current_user.get_id())},
                {"$push": {"savings_goals": new_goal}}
            )
        else:
            # Create a new user document with the savings goal
            mongo.db.users.insert_one({
                "_id": ObjectId(current_user.get_id()),
                "savings_goals": [new_goal],
                "onboarding_complete": True,
                "created_at": datetime.now()
            })

        # Mark onboarding as complete
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {"onboarding_complete": True}}
        )

        flash("Onboarding completed successfully!", "success")
        return redirect(url_for("index"))  # Redirect to the main dashboard

    return render_template("onboarding_step3.html")  # Render step 3 template

@app.route("/onboarding", methods=["GET"])
@login_required
def onboarding():
    """Main onboarding page with multi-step process."""
    # Create budget form with default values
    form = BudgetSettingsForm()
    form.needs_percentage.data = 50
    form.wants_percentage.data = 30
    form.savings_percentage.data = 10
    form.investments_percentage.data = 10
    
    # Get a random financial fact
    financial_fact = get_random_fact()
    
    return render_template("onboarding.html", form=form, financial_fact=financial_fact)

@app.route("/set_budget", methods=["POST"])
@login_required
def set_budget():
    """Handle budget settings submission."""
    if request.method == "POST":
        total_budget = float(request.form.get("total_budget", 0))
        
        # Get category percentages
        budget_settings = {}
        for category in ["Housing", "Food", "Transportation", "Utilities", "Healthcare", 
                         "Personal", "Entertainment", "Savings", "Investments"]:
            if category in request.form:
                budget_settings[category] = float(request.form.get(category, 0))
        
        # Save budget settings to the user's database entry
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.get_id())},
            {"$set": {
                "total_budget": total_budget,
                "budget_categories": budget_settings
            }}
        )
        
        # Check if this is from onboarding
        from_onboarding = request.form.get("from_onboarding") == "true"
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": True, "message": "Budget settings saved successfully!"})
        
        if from_onboarding:
            return redirect(url_for("onboarding", step=2))
        else:
            flash("Budget settings saved successfully!", "success")
            return redirect(url_for("index"))
    
    return redirect(url_for("index"))

@app.route("/restart_onboarding")
@login_required
def restart_onboarding():
    """Restart the onboarding process."""
    # Reset onboarding status
    mongo.db.users.update_one(
        {"_id": ObjectId(current_user.get_id())},
        {"$set": {"onboarding_complete": False}}
    )
    
    flash("Onboarding process restarted. Let's set up your profile again.", "info")
    return redirect(url_for("onboarding"))