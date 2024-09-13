from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import db, load_jobs_from_db, load_job_from_db, add_application_to_db, load_applications_from_db, Application
from sqlalchemy.exc import IntegrityError


from database import db, load_jobs_from_db, load_job_from_db, add_application_to_db, load_applications_from_db, load_application_from_db, update_application_status, User

from database import Application  # Ensure Application model is imported

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root12@localhost/my_vscode_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '12c404489287429bcf017d924b9672ad'  # Required for session management

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
    job = load_job_from_db(id)
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('home'))

    try:
        add_application_to_db(id, data)
    except IntegrityError:
        db.session.rollback()
        flash('Error submitting application. Please try again.', 'danger')
        return redirect(url_for('job_item', job_id=id))

    return render_template("application_submitted.html", data=data, job=job)

@app.route('/job/<int:job_id>')
def job_item(job_id):
    job = load_job_from_db(job_id)
    if job:
        return render_template('jobitem.html', job=job)
    else:
        return "Job not found", 404

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        result = db.session.execute("SELECT * FROM admin_logins WHERE username = :username", {'username': username})
        admin = result.mappings().first()

        if admin and check_password_hash(admin['password'], password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Failed', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    applications = load_applications_from_db()
    count_pending = len([app for app in applications if app['status'] == 'pending'])
    count_accepted = len([app for app in applications if app['status'] == 'accepted'])
    count_rejected = len([app for app in applications if app['status'] == 'rejected'])

    jobs = load_jobs_from_db()
    
    return render_template('admin_dashboard.html', 
                           applications=applications, 
                           count_pending=count_pending, 
                           count_accepted=count_accepted, 
                           count_rejected=count_rejected, 
                           jobs=jobs)

@app.route('/admin/view_applications')
def view_applications():
    if not session.get('admin_logged_in'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('admin_login'))

    applications = Application.query.all()
    return render_template('admin_applications.html', applications=applications)

@app.route('/admin/applications/view/<int:app_id>')
def view_application(app_id):
    if not session.get('admin_logged_in'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('admin_login'))

    application = Application.query.get_or_404(app_id)
    return render_template('view_application.html', application=application)

@app.route('/admin/applications/update_status/<int:app_id>', methods=['POST'])
def update_status(app_id):
    if not session.get('admin_logged_in'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('admin_login'))

    application = Application.query.get_or_404(app_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'accepted', 'rejected']:
        application.status = new_status
        db.session.commit()
        flash('Application status updated successfully!', 'success')
    else:
        flash('Invalid status update.', 'danger')
    return redirect(url_for('view_applications'))

@app.route('/admin/applications/delete/<int:app_id>', methods=['POST'])
def delete_application(app_id):
    if not session.get('admin_logged_in'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('admin_login'))

    application = Application.query.get_or_404(app_id)
    db.session.delete(application)
    db.session.commit()
    flash("Application deleted successfully.", "success")
    return redirect(url_for('view_applications'))

@app.route('/application_submitted')
def application_submitted():
    return render_template('application_submitted.html')

@app.route('/user/application/<int:id>', methods=['GET'])
def application_status(id):
    application = load_application_from_db(id)
    if not application:
        return "Not Found", 404
    return render_template('application_status.html', application=application)

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        session['user_email'] = email
        return redirect(url_for('user_dashboard'))

    return render_template('user_login.html')

@app.route('/user/dashboard')
def user_dashboard():
    email = session.get('user_email')
    if not email:
        return redirect(url_for('user_login'))

    applications = load_applications_from_db()  # Ensure this function returns a list of applications
    user_applications = [app for app in applications if app['email'] == email]
    return render_template('user_dashboard.html', applications=user_applications)

@app.route('/logout')
def logout():
    session.pop('user_logged_in', None)
    return redirect(url_for('login'))

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/add_job', methods=['GET', 'POST'])
def add_job():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        title = request.form.get('title')
        location = request.form.get('location')
        salary = request.form.get('salary')
        currency = request.form.get('currency')
        responsibilities = request.form.get('responsibilities')
        requirements = request.form.get('requirements')

        if not title or not location or not salary or not currency or not responsibilities or not requirements:
            flash('All fields are required!', 'danger')
            return redirect(url_for('add_job'))

        try:
            salary = float(salary)
        except ValueError:
            flash("Invalid salary value. Please enter a numeric value.", 'danger')
            return redirect(url_for('add_job'))

        try:
            db.session.execute(
                """
                INSERT INTO jobs (title, location, salary, currency, responsibilities, requirements)
                VALUES (:title, :location, :salary, :currency, :responsibilities, :requirements)
                """,
                {
                    'title': title,
                    'location': location,
                    'salary': salary,
                    'currency': currency,
                    'responsibilities': responsibilities,
                    'requirements': requirements
                }
            )
            db.session.commit()
            flash('Job added successfully.', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Error adding job. Please try again.', 'danger')
        except Exception as e:
            flash(f'Error adding job: {e}', 'danger')

        return redirect(url_for('admin_dashboard'))

    return render_template('add_job.html')

@app.route('/admin/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        db.session.execute("DELETE FROM jobs WHERE id = :job_id", {'job_id': job_id})
        db.session.commit()
        flash('Job deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting job: {e}', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    job = load_job_from_db(job_id)
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        location = request.form.get('location')
        salary = request.form.get('salary')
        currency = request.form.get('currency')
        responsibilities = request.form.get('responsibilities')
        requirements = request.form.get('requirements')

        if not title or not location or not salary or not currency or not responsibilities or not requirements:
            flash('All fields are required!', 'danger')
            return redirect(url_for('edit_job', job_id=job_id))

        try:
            salary = float(salary)
        except ValueError:
            flash("Invalid salary value. Please enter a numeric value.", 'danger')
            return redirect(url_for('edit_job', job_id=job_id))

        try:
            db.session.execute(
                """
                UPDATE jobs
                SET title = :title,
                    location = :location,
                    salary = :salary,
                    currency = :currency,
                    responsibilities = :responsibilities,
                    requirements = :requirements
                WHERE id = :job_id
                """,
                {
                    'title': title,
                    'location': location,
                    'salary': salary,
                    'currency': currency,
                    'responsibilities': responsibilities,
                    'requirements': requirements,
                    'job_id': job_id
                }
            )
            db.session.commit()
            flash('Job updated successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error updating job: {e}', 'danger')

    return render_template('edit_job.html', job=job)



@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
