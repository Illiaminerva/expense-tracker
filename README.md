# Expense Tracker

A Flask-based expense tracking application that helps users monitor their spending habits using customizable budgeting rules and savings goals. Features an intuitive dashboard with real-time visualizations and spending analysis.

## Features

- **User Authentication**: Secure registration and login system.
- **Expense Management**: Add, edit, and delete expenses seamlessly.
- **Customizable Budgeting**: Adjust the default 50/30/20 rule (Needs/Wants/Savings) to fit your preferences.
- **Savings Goals**: Set savings goals and track your progress with visual indicators.
- **Visual Analytics**: 
  - Monthly spending trends.
  - Category distribution charts.
  - Budget adherence indicators.
  - Savings goal tracking.

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Illiaminerva/expense-tracker.git
cd expense-tracker
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up MongoDB:
- Install MongoDB if you haven't already
- Create a new database
- Note down your MongoDB URI

5. Configure environment variables:
```bash
# Create .env file in project root and add:
MONGO_URI=your_mongodb_uri
SECRET_KEY=your_secret_key
```

6. Run the application:
```bash
python run.py
```

7. Visit `http://127.0.0.1:5000` in your browser

## Usage

1. **Register/Login**: Create an account or login to access your dashboard.
2. **Add Expenses**: 
   - Enter amount, description, and date.
   - Select category (Needs/Wants/Savings).
3. **View Analytics**:
   - Check monthly spending trends.
   - Monitor category distribution.
   - Visualize budget adherence.
   - Track budget adherence.

## Project Structure
```
expense-tracker/
├── app/
│   ├── __init__.py      # App initialization
│   ├── routes.py        # Route handlers
│   ├── forms.py         # Form definitions
│   ├── models.py        # Data models
│   └── templates/       # HTML templates
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables
└── run.py              # Application entry point
```

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: 
  - HTML/CSS
  - JavaScript
  - Chart.js for visualizations
- **Authentication**: Flask-Login
