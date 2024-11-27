from flask_login import UserMixin
from bson.objectid import ObjectId
from app import mongo

class User(UserMixin):
    """User model for managing user sessions."""
    
    def __init__(self, user_id):
        self.id = user_id

    def get_id(self):
        """Return the user ID as a string."""
        return str(self.id)
