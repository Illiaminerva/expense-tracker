from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired()])
    submit = SubmitField("Add Category")


class ExpenseForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired()])
    amount = FloatField("Amount ($)", validators=[DataRequired()])
    category = SelectField(
        "Category",
        choices=[
            ("needs", "Essential Needs"),
            ("wants", "Lifestyle & Wants"),
            ("savings", "Savings & Investments"),
        ],
    )
    date = DateField("Transaction Date", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("Record Expense")
