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
- Docker and Docker Compose (if running locally)
- Git

### Access Options

#### Option 1: Live Application
Access the live application at: [[INSERT_YOUR_LIVE_LINK](https://expense-tracker-application-bccee6223f0f.herokuapp.com/)]

#### Option 2: Local Development with Docker
1. Clone the repository:
```bash
git clone https://github.com/Illiaminerva/expense-tracker.git
cd expense-tracker
```

2. Build and start the Docker containers:
```bash
docker-compose up --build
```

3. Visit `http://localhost:5001` in your browser.

## Testing

### Setup Testing Environment
1. Install testing requirements:
```bash
pip install -r requirements-test.txt
```

2. Run the test suite:
```bash
pytest tests/
```

The test suite covers:
- User authentication (`tests/test_auth.py`)
- Expense management (`tests/test_expenses.py`)
- Budget calculations (`tests/test_budget.py`)
- Database operations (`tests/test_db.py`)
- Core functionality (`tests/test_core.py`)

## Project Structure

```
expense-tracker/
├── app/
│   ├── __init__.py                  # App initialization and configuration
│   ├── routes.py                    # Route handlers and business logic
│   ├── forms.py                     # Form definitions and validation
│   ├── models.py                    # Data models and database interactions
│   ├── static/                      # CSS
│   └── templates/                   # HTML templates
├── tests/
│   ├── conftest.py                  # Test configurations and fixtures
│   ├── test_auth.py                 # Authentication tests
│   ├── test_budget.py              # Budget calculation tests
│   ├── test_core.py                # Core functionality tests
│   ├── test_db.py                  # Database operation tests
│   └── test_expenses.py            # Expense management tests
├── Dockerfile                       # Application container definition
├── docker-compose.yml              # Container orchestration
├── requirements.txt                # Project dependencies
├── requirements-test.txt           # Testing dependencies
└── .env.example                     # Example environment variables
```


## Technologies Used

- **Backend**:
  - Flask (Python web framework)
  - PyMongo (MongoDB integration)
  - Flask-Login (Authentication)
  - Flask-WTF (Form handling and validation)
  - Python-dateutil (Date manipulation)
- **Database**: MongoDB
- **Testing**:
  - Pytest
  - Pytest-mock
  - Coverage.py
