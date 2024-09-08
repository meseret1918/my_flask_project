from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from sqlalchemy import text
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

# Define the User model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f'<User {self.username}>'

# Define the Application model
class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    linkedin_url = db.Column(db.String(200))
    education = db.Column(db.String(200))
    work_experience = db.Column(db.String(500))
    resume_url = db.Column(db.String(200))

    def __repr__(self):
        return f'<Application {self.full_name}>'

# Define the Job model
class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    salary = db.Column(db.Float)
    currency = db.Column(db.String(10))
    responsibilities = db.Column(db.Text)
    requirements = db.Column(db.Text)

    # Define relationship to Application
    applications = db.relationship('Application', backref='job', lazy=True)

    def __repr__(self):
        return f'<Job {self.title}>'

# Job-related functions
def load_jobs_from_db():
    try:
        with app.app_context():
            result = db.session.execute(text('SELECT * FROM jobs'))
            jobs = [dict(row) for row in result.mappings().all()]
            return jobs
    except Exception as e:
        print(f"Error loading jobs: {e}")
        return []

def load_job_from_db(id):
    try:
        with app.app_context():
            result = db.session.execute(text("SELECT * FROM jobs WHERE id = :id"), {'id': id})
            row = result.mappings().first()
            if row:
                return dict(row)
            return None
    except Exception as e:
        print(f"Error loading job with ID {id}: {e}")
        return None

def add_application_to_db(job_id, application):
    try:
        with app.app_context():
            query = text(
                "INSERT INTO applications (job_id, full_name, email, linkedin_url, education, work_experience, resume_url) "
                "VALUES (:job_id, :full_name, :email, :linkedin_url, :education, :work_experience, :resume_url)"
            )
            db.session.execute(query, {
                "job_id": job_id,
                "full_name": application.get("full_name"),
                "email": application.get("email"),
                "linkedin_url": application.get("linkedin_url"),
                "education": application.get("education"),
                "work_experience": application.get("work_experience"),
                "resume_url": application.get("resume_url")
            })
            db.session.commit()
    except Exception as e:
        print(f"Error adding application: {e}")
        db.session.rollback()

def load_applications_from_db():
    try:
        with app.app_context():
            result = db.session.execute(text('SELECT * FROM applications'))
            applications = [dict(row) for row in result.mappings().all()]
            return applications
    except Exception as e:
        print(f"Error loading applications: {e}")
        return []

def load_application_from_db(id):
    try:
        with app.app_context():
            result = db.session.execute(text("SELECT * FROM applications WHERE id = :id"), {'id': id})
            row = result.mappings().first()
            if row:
                return dict(row)
            return None
    except Exception as e:
        print(f"Error loading application with ID {id}: {e}")
        return None

def update_application_status(id, status):
    try:
        with app.app_context():
            query = text("UPDATE applications SET status = :status WHERE id = :id")
            db.session.execute(query, {'status': status, 'id': id})
            db.session.commit()
    except Exception as e:
        print(f"Error updating application status for ID {id}: {e}")
        db.session.rollback()

# User-related functions
def get_all_users():
    try:
        with app.app_context():
            return User.query.all()
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def get_user_by_id(user_id):
    try:
        with app.app_context():
            return User.query.get(user_id)
    except Exception as e:
        print(f"Error fetching user with ID {user_id}: {e}")
        return None

def add_user(username, password):
    try:
        with app.app_context():
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
    except Exception as e:
        print(f"Error adding user: {e}")
        db.session.rollback()

def update_user(user_id, username=None, password=None):
    try:
        with app.app_context():
            user = User.query.get(user_id)
            if user:
                if username:
                    user.username = username
                if password:
                    user.password = generate_password_hash(password)
                db.session.commit()
            return user
    except Exception as e:
        print(f"Error updating user with ID {user_id}: {e}")
        db.session.rollback()
        return None

def delete_user(user_id):
    try:
        with app.app_context():
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
    except Exception as e:
        print(f"Error deleting user with ID {user_id}: {e}")
        db.session.rollback()
