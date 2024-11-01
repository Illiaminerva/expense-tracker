from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, mongo, login_manager
from app.forms import LoginForm, RegistrationForm, ExpenseForm, CategoryForm
from app.models import User
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route("/")
@login_required
def index():
    expenses = list(mongo.db.expenses.find({"user_id": current_user.get_id()}))
    categories = mongo.db.expenses.distinct("category")
    total_expenses = sum(expense["amount"] for expense in expenses)
    form = ExpenseForm()
    return render_template(
        "index.html",
        form=form,
        expenses=expenses,
        total_expenses=total_expenses,
        categories=categories,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and check_password_hash(user["password"], form.password.data):
            user_obj = User(str(user["_id"]))
            login_user(user_obj)
            return redirect(url_for("index"))
        flash("Invalid email or password")
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user is None:
            hash_pass = generate_password_hash(form.password.data)
            mongo.db.users.insert_one({"email": form.email.data, "password": hash_pass})
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Email already registered", "error")
    else:
        flash("Please correct the highlighted fields.", "error")
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/add_expense", methods=["POST"])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        mongo.db.expenses.insert_one(
            {
                "user_id": current_user.get_id(),
                "description": form.description.data,
                "amount": float(form.amount.data),
                "category": form.category.data,
                "date": str(form.date.data),
            }
        )
        flash("Expense added successfully!")
    return redirect(url_for("index"))


@app.route("/delete_category/<category_id>")
@login_required
def delete_category(category_id):
    mongo.db.categories.delete_one(
        {"_id": ObjectId(category_id), "user_id": current_user.get_id()}
    )
    flash("Category deleted successfully!")
    return redirect(url_for("categories"))


@app.route("/edit_expense/<expense_id>", methods=["POST"])
@login_required
def edit_expense(expense_id):
    form = ExpenseForm()
    valid_categories = [choice[0] for choice in form.category.choices]

    if request.form["category"] not in valid_categories:
        flash("Invalid category selected!", "error")
        return redirect(url_for("index"))

    updated_expense = {
        "description": request.form["description"],
        "amount": float(request.form["amount"]),
        "category": request.form["category"],
        "date": request.form["date"],
    }
    mongo.db.expenses.update_one(
        {"_id": ObjectId(expense_id), "user_id": current_user.get_id()},
        {"$set": updated_expense},
    )
    flash("Expense updated successfully!")
    return redirect(url_for("index"))


@app.route("/delete_expense/<expense_id>")
@login_required
def delete_expense(expense_id):
    mongo.db.expenses.delete_one(
        {"_id": ObjectId(expense_id), "user_id": current_user.get_id()}
    )
    flash("Expense deleted successfully!")
    return redirect(url_for("index"))


@app.route("/summary")
@login_required
def summary():
    expenses = list(mongo.db.expenses.find({"user_id": current_user.get_id()}))
    total_expenses = sum(e['amount'] for e in expenses)
    
    end_date = datetime.now()
    start_date = end_date - relativedelta(months=11)
    
    recent_expenses = [
        expense for expense in expenses 
        if datetime.strptime(expense['date'], '%Y-%m-%d') >= start_date
    ]
    monthly_average = sum(e['amount'] for e in recent_expenses) / 12

    monthly_totals = {}
    current_date = start_date
    while current_date <= end_date:
        month_key = current_date.strftime('%Y-%m')
        monthly_totals[month_key] = 0.0
        current_date += relativedelta(months=1)
    
    for expense in expenses:
        date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
        if start_date <= date_obj <= end_date:
            month_key = date_obj.strftime('%Y-%m')
            monthly_totals[month_key] += expense['amount']
    
    sorted_months = sorted(monthly_totals.keys())
    
    time_data = {
        "labels": [datetime.strptime(m, '%Y-%m').strftime('%B %Y') for m in sorted_months],
        "values": [monthly_totals[m] for m in sorted_months]
    }
    
    expenses_by_category = defaultdict(list)
    
    for expense in expenses:
        date_obj = datetime.strptime(expense['date'], '%Y-%m-%d')
        category = expense['category']
        amount = expense['amount']
        expenses_by_category[category].append({
            'date': date_obj.strftime('%Y-%m-%d'),
            'amount': amount
        })
    
    category_data = {
        "labels": [],
        "values": [],
        "dates": [],
        "monthly_data": {}  
    }
    
    for category, expense_list in expenses_by_category.items():
        monthly_totals = defaultdict(float)
        for expense in expense_list:
            date = datetime.strptime(expense['date'], '%Y-%m-%d')
            month_key = date.strftime('%Y-%m')
            monthly_totals[month_key] += expense['amount']
        
        category_data["labels"].append(category)
        category_data["values"].append(sum(expense['amount'] for expense in expense_list))
        category_data["dates"].extend([expense['date'] for expense in expense_list])
        category_data["monthly_data"][category] = dict(monthly_totals)

    return render_template(
        "summary.html",
        total_expenses=total_expenses,
        monthly_average=monthly_average,
        time_data=time_data,
        category_data=category_data
    )
