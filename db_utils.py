from database import db
from database import User  # Adjust if your User model is in another file

def get_all_users():
    try:
        return User.query.all()
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
