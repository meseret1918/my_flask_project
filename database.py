from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app
from sqlalchemy import text

db = SQLAlchemy()

def load_jobs_from_db():
    with app.app_context():
        result = db.session.execute(text('SELECT * FROM jobs'))
        jobs = [dict(row) for row in result.mappings().all()]
        return jobs

def load_job_from_db(id):
    with app.app_context():
        result = db.session.execute(text("SELECT * FROM jobs WHERE id = :val"), {'val': id})
        rows = result.mappings().all()
        if not rows:
            return None
        return dict(rows[0])

def add_application_to_db(job_id, application):
    application = dict(application)
    with app.app_context():
        query = text(
            "INSERT INTO applications (job_id, full_name, email, linkedin_url, education, work_experience, resume_url) VALUES (:job_id, :full_name, :email, :linkedin_url, :education, :work_experience, :resume_url)"
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
