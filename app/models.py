from flask_login import UserMixin
from bson.objectid import ObjectId
from app import mongo

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    def get_id(self):
        return str(self.id)
