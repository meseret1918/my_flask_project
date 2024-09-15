from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy for ORM (Object Relational Mapping)
from flask import current_app as app  # Import current_app to access the application context
from sqlalchemy import text  # Import text for raw SQL queries
from werkzeug.security import generate_password_hash  # Import for hashing passwords

db = SQLAlchemy()  # Initialize SQLAlchemy

# Define the User model
class User(db.Model):
    __tablename__ = 'users'  # Name of the table in the database
    
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    username = db.Column(db.String(128), nullable=False, unique=True)  # Username column
    password = db.Column(db.String(128), nullable=False)  # Password column

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)  # Hash the password on initialization

    def __repr__(self):
        return f'<User {self.username}>'  # Representation of the User object

# Define the Application model
class Application(db.Model):
    __tablename__ = 'applications'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    full_name = db.Column(db.String(100), nullable=False)  # Applicant's full name
    email = db.Column(db.String(100), nullable=False)  # Applicant's email
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)  # Foreign key linking to the jobs table
    status = db.Column(db.String(20), default='pending')  # Status of the application
    linkedin_url = db.Column(db.String(200))  # LinkedIn URL
    education = db.Column(db.String(200))  # Education details
    work_experience = db.Column(db.String(500))  # Work experience details
    resume_url = db.Column(db.String(200))  # Resume URL

    def __repr__(self):
        return f'<Application {self.full_name}>'  # Representation of the Application object

# Define the Job model
class Job(db.Model):
    __tablename__ = 'jobs'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    title = db.Column(db.String(100), nullable=False)  # Job title
    location = db.Column(db.String(100))  # Job location
    salary = db.Column(db.Float)  # Job salary
    currency = db.Column(db.String(10))  # Currency of the salary
    responsibilities = db.Column(db.Text)  # Job responsibilities
    requirements = db.Column(db.Text)  # Job requirements

    # Define relationship to Application
    applications = db.relationship('Application', backref='job', lazy=True)  # One-to-many relationship with applications

    def __repr__(self):
        return f'<Job {self.title}>'  # Representation of the Job object

# Job-related functions
def load_jobs_from_db():
    try:
        with app.app_context():  # Ensure code runs within the application context
            result = db.session.execute(text('SELECT * FROM jobs'))  # Execute raw SQL query to fetch all jobs
            jobs = [dict(row) for row in result.mappings().all()]  # Convert result to a list of dictionaries
            return jobs
    except Exception as e:
        print(f"Error loading jobs: {e}")  # Print error if any
        return []

def load_job_from_db(id):
    try:
        with app.app_context():  # Ensure code runs within the application context
            result = db.session.execute(text("SELECT * FROM jobs WHERE id = :id"), {'id': id})  # Execute raw SQL query to fetch a job by ID
            row = result.mappings().first()  # Fetch the first row of the result
            if row:
                return dict(row)  # Convert row to a dictionary
            return None
    except Exception as e:
        print(f"Error loading job with ID {id}: {e}")  # Print error if any
        return None

def add_application_to_db(job_id, application):
    try:
        with app.app_context():  # Ensure code runs within the application context
            query = text(
                "INSERT INTO applications (job_id, full_name, email, linkedin_url, education, work_experience, resume_url) "
                "VALUES (:job_id, :full_name, :email, :linkedin_url, :education, :work_experience, :resume_url)"
            )  # Define the SQL query for inserting a new application
            db.session.execute(query, {
                "job_id": job_id,
                "full_name": application.get("full_name"),
                "email": application.get("email"),
                "linkedin_url": application.get("linkedin_url"),
                "education": application.get("education"),
                "work_experience": application.get("work_experience"),
                "resume_url": application.get("resume_url")
            })  # Execute the query with the provided data
            db.session.commit()  # Commit the transaction
    except Exception as e:
        print(f"Error adding application: {e}")  # Print error if any
        db.session.rollback()  # Rollback transaction on error

def load_applications_from_db():
    try:
        with app.app_context():  # Ensure code runs within the application context
            result = db.session.execute(text('SELECT * FROM applications'))  # Execute raw SQL query to fetch all applications
            applications = [dict(row) for row in result.mappings().all()]  # Convert result to a list of dictionaries
            return applications
    except Exception as e:
        print(f"Error loading applications: {e}")  # Print error if any
        return []

def load_application_from_db(id):
    try:
        with app.app_context():  # Ensure code runs within the application context
            result = db.session.execute(text("SELECT * FROM applications WHERE id = :id"), {'id': id})  # Execute raw SQL query to fetch an application by ID
            row = result.mappings().first()  # Fetch the first row of the result
            if row:
                return dict(row)  # Convert row to a dictionary
            return None
    except Exception as e:
        print(f"Error loading application with ID {id}: {e}")  # Print error if any
        return None

def update_application_status(id, status):
    try:
        with app.app_context():  # Ensure code runs within the application context
            query = text("UPDATE applications SET status = :status WHERE id = :id")  # Define the SQL query for updating application status
            db.session.execute(query, {'status': status, 'id': id})  # Execute the query with the provided data
            db.session.commit()  # Commit the transaction
    except Exception as e:
        print(f"Error updating application status for ID {id}: {e}")  # Print error if any
        db.session.rollback()  # Rollback transaction on error

# User-related functions
def get_all_users():
    try:
        with app.app_context():  # Ensure code runs within the application context
            return User.query.all()  # Fetch all users from the database
    except Exception as e:
        print(f"Error fetching users: {e}")  # Print error if any
        return []

def get_user_by_id(user_id):
    try:
        with app.app_context():  # Ensure code runs within the application context
            return User.query.get(user_id)  # Fetch a user by ID
    except Exception as e:
        print(f"Error fetching user with ID {user_id}: {e}")  # Print error if any
        return None

def add_user(username, password):
    try:
        with app.app_context():  # Ensure code runs within the application context
            new_user = User(username=username, password=password)  # Create a new User instance
            db.session.add(new_user)  # Add the new user to the session
            db.session.commit()  # Commit the transaction
    except Exception as e:
        print(f"Error adding user: {e}")  # Print error if any
        db.session.rollback()  # Rollback transaction on error

def update_user(user_id, username=None, password=None):
    try:
        with app.app_context():  # Ensure code runs within the application context
            user = User.query.get(user_id)  # Fetch the user by ID
            if user:
                if username:
                    user.username = username  # Update username if provided
                if password:
                    user.password = generate_password_hash(password)  # Update password if provided
                db.session.commit()  # Commit the transaction
            return user
    except Exception as e:
        print(f"Error updating user with ID {user_id}: {e}")  # Print error if any
        db.session.rollback()  # Rollback transaction on error
        return None

def delete_user(user_id):
    try:
        with app.app_context():  # Ensure code runs within the application context
            user = User.query.get(user_id)  # Fetch the user by ID
            if user:
                db.session.delete(user)  # Delete the user from the session
                db.session.commit()  # Commit the transaction
    except Exception as e:
        print(f"Error deleting user with ID {user_id}: {e}")  # Print error if any
        db.session.rollback()  # Rollback transaction on error
