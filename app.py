from flask import Flask, render_template, jsonify, request, abort
from database import db, load_jobs_from_db, load_job_from_db, add_application_to_db



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root12@localhost/my_vscode_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route("/")
def home():
  jobs = load_jobs_from_db()
  return render_template("home.html", jobs=jobs, show_back_button=False)

@app.route("/api/jobs")
def list_jobs():
  jobs = load_jobs_from_db()
  return jsonify(jobs)

@app.route("/api/job/<int:id>")
def list_job(id):
  job = load_job_from_db(id)
  if not job:
    return "Not Found", 404
  else:
    return render_template("jobpage.html", job=job, show_back_button=True)

@app.route("/job/<int:id>/apply", methods=['POST'])
def apply_job(id):
    data = {
        'full_name': request.form.get('full_name'),
        'email': request.form.get('email'),
        'linkedin_url': request.form.get('linkedin_url'),
        'education': request.form.get('education'),
        'work_experience': request.form.get('work_experience'),
        'resume_url': request.form.get('resume_url'),
    }
    print("Form data:", data)  # Debug print to check data
    job = load_job_from_db(id)
    add_application_to_db(id, data)
    return render_template("application_submitted.html", data=data, job=job, show_back_button=True)


@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
