from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_object('config.Config')

mongo = PyMongo(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes
