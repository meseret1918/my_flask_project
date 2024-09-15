# Import necessary modules from Flask and other libraries
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import db, load_jobs_from_db, load_job_from_db, add_application_to_db, load_applications_from_db, Application
from sqlalchemy.exc import IntegrityError
from database import load_application_from_db


# Initialize the Flask application
app = Flask(__name__)

# Configure the application with SQLAlchemy database URI and session secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root12@localhost/my_vscode_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable Flask-SQLAlchemy event system
app.secret_key = '12c404489287429bcf017d924b9672ad'  # Secret key required for session management

# Initialize the SQLAlchemy extension with the Flask app
db.init_app(app)

# Route for the homepage that lists all jobs
@app.route("/")
def home():
    jobs = load_jobs_from_db()  # Retrieve jobs from the database
    return render_template("home.html", jobs=jobs)  # Render the home page template with jobs

# API route to list all jobs in JSON format
@app.route("/api/jobs")
def list_jobs():
    jobs = load_jobs_from_db()  # Retrieve jobs from the database
    return jsonify(jobs)  # Return jobs as JSON

# API route to get details of a specific job by ID
@app.route("/api/job/<int:id>")
def list_job(id):
    job = load_job_from_db(id)  # Retrieve job by ID from the database
    if not job:
        return "Not Found", 404  # Return 404 if job not found
    return render_template("jobpage.html", job=job)  # Render the job details page
# Route for applying to a specific job
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
    job = load_job_from_db(id)  # Retrieve job by ID from the database
    if not job:
        flash('Job not found', 'danger')  # Flash error message if job not found
        return redirect(url_for('home'))  # Redirect to home page

    try:
        add_application_to_db(id, data)  # Attempt to add application to the database
    except IntegrityError:
        db.session.rollback()  # Rollback transaction on error
        flash('Error submitting application. Please try again.', 'danger')  # Flash error message
        return redirect(url_for('job_item', job_id=id))  # Redirect to job details page

    return render_template("application_submitted.html", data=data, job=job)  # Render application submitted page

# Route for viewing a specific job by ID
@app.route('/job/<int:job_id>')
def job_item(job_id):
    job = load_job_from_db(job_id)  # Retrieve job by ID from the database
    if job:
        return render_template('jobitem.html', job=job)  # Render the job item page
    else:
        return "Job not found", 404  # Return 404 if job not found
# Route for admin login page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        result = db.session.execute("SELECT * FROM admin_logins WHERE username = :username", {'username': username})
        admin = result.mappings().first()  # Retrieve admin user from the database

        if admin and check_password_hash(admin['password'], password):  # Check password hash
            session['admin_logged_in'] = True  # Set session variable
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
        else:
            flash('Login Failed', 'danger')  # Flash error message
            return redirect(url_for('admin_login'))  # Redirect to admin login page

    return render_template('admin_login.html')  # Render admin login page template

# Route for admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))  # Redirect to login if not logged in

    applications = load_applications_from_db()  # Retrieve all applications from the database
    count_pending = len([app for app in applications if app['status'] == 'pending'])
    count_accepted = len([app for app in applications if app['status'] == 'accepted'])
    count_rejected = len([app for app in applications if app['status'] == 'rejected'])

    jobs = load_jobs_from_db()  # Retrieve all jobs from the database

    return render_template('admin_dashboard.html', 
                           applications=applications, 
                           count_pending=count_pending, 
                           count_accepted=count_accepted, 
                           count_rejected=count_rejected, 
                           jobs=jobs)  # Render admin dashboard template

# Route for viewing all applications
@app.route('/admin/view_applications')
def view_applications():
    if not session.get('admin_logged_in'):
        flash('Please log in to access this page.', 'warning')  # Flash warning message
        return redirect(url_for('admin_login'))  # Redirect to admin login page

    applications = Application.query.all()  # Retrieve all applications from the database
    return render_template('admin_applications.html', applications=applications)  # Render applications page

# Route for viewing a specific application by ID
@app.route('/admin/applications/view/<int:app_id>')
def view_application(app_id):
    if not session.get('admin_logged_in'):
        flash('Please log in to access this page.', 'warning')  # Flash warning message
        return redirect(url_for('admin_login'))  # Redirect to admin login page

    application = Application.query.get_or_404(app_id)  # Retrieve application by ID or 404 if not found
    return render_template('view_application.html', application=application)  # Render application view page

# Route for updating the status of a specific application
@app.route('/admin/applications/update/<int:app_id>', methods=['GET', 'POST'])
def update_application(app_id):
    application = Application.query.get_or_404(app_id)  # Retrieve application by ID or 404 if not found
    
    if request.method == 'POST':
        new_status = request.form.get('status').lower()  # Get new status from form and convert to lowercase
        if new_status not in ['pending', 'accepted', 'rejected']:
            flash('Invalid status update.', 'danger')  # Flash error message if status is invalid
            return redirect(url_for('view_applications'))  # Redirect to view applications

        application.status = new_status.capitalize()  # Update application status
        db.session.commit()  # Commit changes to the database
        flash('Application status updated successfully!', 'success')  # Flash success message
        return redirect(url_for('view_applications'))  # Redirect to view applications

    return render_template('update_application.html', application=application)  # Render application update page

# Route for deleting a specific application by ID
@app.route('/admin/applications/delete/<int:app_id>', methods=['POST'])
def delete_application(app_id):
    if not session.get('admin_logged_in'):
        flash('Please log in to access this page.', 'warning')  # Flash warning message
        return redirect(url_for('admin_login'))  # Redirect to admin login page

    application = Application.query.get_or_404(app_id)  # Retrieve application by ID or 404 if not found
    db.session.delete(application)  # Delete application from the database
    db.session.commit()  # Commit changes to the database
    flash("Application deleted successfully.", "success")  # Flash success message
    return redirect(url_for('view_applications'))  # Redirect to view applications

# Route for the application submission confirmation page
@app.route('/application_submitted')
def application_submitted():
    return render_template('application_submitted.html')  # Render application submitted page

# Route for viewing application status by ID
@app.route('/user/application/<int:id>', methods=['GET'])
def application_status(id):
    application = load_application_from_db(id)  # Retrieve application by ID from the database
    if not application:
        return "Not Found", 404  # Return 404 if application not found
    return render_template('application_status.html', application=application)  # Render application status page

# Route for user login page
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        session['user_email'] = email  # Store user email in session
        return redirect(url_for('user_dashboard'))  # Redirect to user dashboard

    return render_template('user_login.html')  # Render user login page

# Route for user dashboard
@app.route('/user/dashboard')
def user_dashboard():
    email = session.get('user_email')
    if not email:
        return redirect(url_for('user_login'))  # Redirect to login if not logged in

    applications = load_applications_from_db()  # Retrieve all applications from the database
    user_apps = [app for app in applications if app['email'] == email]  # Filter applications by user email
    return render_template('user_dashboard.html', applications=user_apps)  # Render user dashboard page

# Route for user logout
@app.route('/logout')
def logout():
    # Remove 'user_logged_in' from the session to log out the user
    session.pop('user_logged_in', None)
    return redirect(url_for('login'))  # Redirect to the login page

# Route for admin logout
@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    # Remove 'admin_logged_in' from the session to log out the admin
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))  # Redirect to the admin login page

# Route for adding a job (admin only)
@app.route('/admin/add_job', methods=['GET', 'POST'])
def add_job():
    # Check if the admin is logged in
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))  # Redirect to admin login if not logged in

    if request.method == 'POST':
        # Retrieve job details from the form
        title = request.form.get('title')
        location = request.form.get('location')
        salary = request.form.get('salary')
        currency = request.form.get('currency')
        responsibilities = request.form.get('responsibilities')
        requirements = request.form.get('requirements')

        # Validate that all fields are filled
        if not title or not location or not salary or not currency or not responsibilities or not requirements:
            flash('All fields are required!', 'danger')  # Show error message
            return redirect(url_for('add_job'))  # Redirect back to the add job page

        try:
            # Convert salary to float and validate
            salary = float(salary)
        except ValueError:
            flash("Invalid salary value. Please enter a numeric value.", 'danger')  # Show error message
            return redirect(url_for('add_job'))  # Redirect back to the add job page

        try:
            # Insert job into the database
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
            db.session.commit()  # Commit the transaction
            flash('Job added successfully.', 'success')  # Show success message
        except IntegrityError:
            db.session.rollback()  # Rollback in case of an error
            flash('Error adding job. Please try again.', 'danger')  # Show error message
        except Exception as e:
            flash(f'Error adding job: {e}', 'danger')  # Show detailed error message

        return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard

    return render_template('add_job.html')  # Render the add job template

# Route for deleting a job (admin only)
@app.route('/admin/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    # Check if the admin is logged in
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))  # Redirect to admin login if not logged in

    try:
        # Delete job from the database
        db.session.execute("DELETE FROM jobs WHERE id = :job_id", {'job_id': job_id})
        db.session.commit()  # Commit the transaction
        flash('Job deleted successfully.', 'success')  # Show success message
    except Exception as e:
        flash(f'Error deleting job: {e}', 'danger')  # Show detailed error message

    return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard

# Route for editing a job (admin only)
@app.route('/admin/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    # Check if the admin is logged in
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))  # Redirect to admin login if not logged in

    # Load the job details from the database
    job = load_job_from_db(job_id)
    if not job:
        flash('Job not found.', 'danger')  # Show error message if job not found
        return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard

    if request.method == 'POST':
        # Retrieve updated job details from the form
        title = request.form.get('title')
        location = request.form.get('location')
        salary = request.form.get('salary')
        currency = request.form.get('currency')
        responsibilities = request.form.get('responsibilities')
        requirements = request.form.get('requirements')

        # Validate that all fields are filled
        if not title or not location or not salary or not currency or not responsibilities or not requirements:
            flash('All fields are required!', 'danger')  # Show error message
            return redirect(url_for('edit_job', job_id=job_id))  # Redirect back to the edit job page

        try:
            # Convert salary to float and validate
            salary = float(salary)
        except ValueError:
            flash("Invalid salary value. Please enter a numeric value.", 'danger')  # Show error message
            return redirect(url_for('edit_job', job_id=job_id))  # Redirect back to the edit job page

        try:
            # Update job details in the database
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
            db.session.commit()  # Commit the transaction
            flash('Job updated successfully.', 'success')  # Show success message
            return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard
        except Exception as e:
            flash(f'Error updating job: {e}', 'danger')  # Show detailed error message

    return render_template('edit_job.html', job=job)  # Render the edit job template with job details

# Route for the courses page
@app.route('/courses')
def courses():
    return render_template('courses.html')  # Render the courses template

# Route for the pricing page
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')  # Render the pricing template

# Route for the FAQs page
@app.route('/faqs')
def faqs():
    return render_template('faqs.html')  # Render the FAQs template

# Main entry point to run the Flask application
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5001)  # Run the app with debug mode enabled

