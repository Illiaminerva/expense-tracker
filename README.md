# Expense Tracker

A Flask-based expense tracking application that helps users monitor their spending habits using customizable budgeting rules and savings goals. Features an intuitive dashboard with real-time visualizations and spending analysis.

## Features

- **User Authentication**: Secure registration and login system.
- **Expense Management**: Add, edit, and delete expenses seamlessly.
- **Customizable Budgeting**: Manually split your income into Needs/Wants/Savings/Investments to fit your preferences.
- **Savings Goals**: Set multiple savings goals and track your progress with visual indicators.
- **Manual assignment of Savings/Investments**: Ability to manually dedicate your expenses to one of your savings goals.
- **Visual Analytics**: 
  - Monthly spending trends.
  - Category distribution charts.
  - Budget adherence indicators.
  - Savings goal tracking.

## Quick Start

### Prerequisites

- Python 3.11+
- Docker
- MongoDB
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Illiaminerva/expense-tracker.git
cd expense-tracker
```
2. Set up MongoDB:
- Install MongoDB if you haven't already
- Create a new database
- Note down your MongoDB URI

3. Build and start the Docker containers:
```bash
docker-compose up -d
```

4. Visit your localhost in the browser.

## Run Tests (OUTDATED, to be fixed soon)

To ensure everything is working correctly, run the test suite:
```bash
pytest
```
This will execute all tests, including functionality for savings goals, expense management, and budgeting rules.

## Usage

1. **Register/Login**: Create an account or login to access your dashboard.
2. **Set Budget Allocations**:
   - Allocate percentages to Needs, Wants, Savings, and Investments categories.
   - The system automatically calculates the Investment percentage based on your other allocations.
3. **Add Expenses**: 
   - Enter the amount, description, and date.
   - Select the appropriate category.
   - Optionally link to a savings goal.
4. **Create Savings Goals**:
   - Set specific financial targets with deadlines.
   - Track progress with visual charts.
   - Link relevant expenses to goals. 
5. **View Analytics**:
   - Check monthly spending trends.
   - Monitor category distribution.
   - Visualize budget adherence.
   - Track progress toward savings goals.

## Project Structure
```
expense-tracker/
├── app/
│   ├── __init__.py                  # App initialization and configuration
│   ├── routes.py                    # Route handlers and business logic
│   ├── forms.py                     # Form definitions and validation
│   ├── models.py                    # Data models and database interactions
│   ├── static/                      # CSS
│   │   ├── styles.css               # Stylesheets
│   └── templates/                   # HTML templates
│       ├── base.html                # Base template with common elements
│       ├── budget_settings.html     # Budget settings template
│       ├── index.html               # Dashboard template
│       ├── login.html               # Login template
│       ├── onboarding.html          # Onboarding template
│       ├── register.html            # Register template
│       ├── set_savings_goal.html    # Savings goals templates
│       └── summary.html             # Analytics and reports
├── Dockerfile                       # Application container definition
├── docker-compose.yml               # Container definition
├── requirements.txt                 # Project dependencies
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore rules
└── run.py                           # Application entry point
```

## Technologies Used

- **Backend**:
  - Flask (Python web framework)
  - PyMongo (MongoDB integration)
  - Flask-Login (Authentication)
  - Flask-WTF (Form handling and validation)
  - Python-dateutil (Date manipulation)
- **Database**: MongoDB (will later be changed to Postgresql)
- **Frontend**: 
  - HTML/CSS
  - JavaScript
  - Chart.js for visualizations
  - Bootstrap
