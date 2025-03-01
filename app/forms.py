from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from datetime import date


class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """Form for user registration."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class ExpenseForm(FlaskForm):
    """Form for adding and editing expenses."""
    description = StringField("Description", validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField(
        "Category",
        choices=[
            ("Needs", "Needs"),
            ("Wants", "Wants"),
            ("Savings", "Savings"),
            ("Investments", "Investments")
        ],
        validators=[DataRequired()],
    )
    date = DateField("Date", validators=[DataRequired()])
    # Note: goal_id will be added dynamically in the template
    submit = SubmitField('Add Expense')


class BudgetSettingsForm(FlaskForm):
    """Form for setting budget percentages."""
    needs_percentage = FloatField('Needs (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    wants_percentage = FloatField('Wants (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    savings_percentage = FloatField('Savings (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    investments_percentage = FloatField('Investments (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Save Settings')
