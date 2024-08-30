# Expense Tracker

Expense Tracker is a simple web application that allows users to track their expenses. Users can add, edit, and delete expenses, and categorize them to better understand their spending habits. The application also provides a summary of expenses by category and over time, helping users to manage their finances more effectively.

## Features

- **User Authentication**: Secure login and registration for users.
- **Add Expenses**: Users can add new expenses with a description, amount, category, and date.
- **Edit and Delete Expenses**: Users can easily edit or delete existing expenses.
- **Expense Categories**: Users can select from existing categories or add a new one.
- **Summary Reports**: Visual representation of expenses by category and over time using charts.

## Installation

To run this project locally, follow the steps below:

### 1. Clone the repository
First, clone this repository to your local machine using the following command:

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/YOUR-REPOSITORY-NAME.git
```

### 2. Navigate to the project directory

```bash
cd YOUR-REPOSITORY-NAME
```

### 3. Create and activate a virtual environment

It's a good practice to use a virtual environment for your Python projects to manage dependencies. You can create and activate a virtual environment with:

```bash
python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

### 4. Install dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 5. Set up MongoDB

This application uses MongoDB to store data. Follow the steps below to set up MongoDB:

- Install MongoDB on your local machine. You can download it from [MongoDB's official website](https://www.mongodb.com/try/download/community).
- Start the MongoDB server by running `mongod` in your terminal.
- Create a new database and collection for the expense tracker. You can do this using the MongoDB shell:

```bash
mongo
use expense_tracker
db.createCollection('expenses')
```

- Update your `config.py` file with the MongoDB URI and database name:

```python
MONGO_URI = "mongodb://localhost:27017/expense_tracker"
```

### 6. Run the application

To start the application, simply run:

```bash
python run.py
```

By default, the application will be available at `http://127.0.0.1:5000/`.

## Usage

- **Home Page**: After logging in, you'll see a list of your expenses and a form to add new expenses.
- **Adding Expenses**: Fill in the description, amount, category, and date to add a new expense. You can either select a category from the dropdown or enter a new category in the provided field.
- **Editing/Deleting Expenses**: Each expense has options to edit or delete it directly from the list.
- **Summary Page**: View graphical summaries of your expenses by category and over time.
