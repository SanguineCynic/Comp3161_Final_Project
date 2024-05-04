import os
from app import app, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.forms import LoginForm, UploadForm, CourseForm, UserForm
from flask import send_from_directory
from flask_login import logout_user
from datetime import datetime
import secrets
from werkzeug.security import check_password_hash
import mysql.connector
from enum import Enum
from flask_bcrypt import Bcrypt
import secrets
import string


bcrypt = Bcrypt()

class UserType(Enum):
    STUDENT = 'student'
    LECTURER = 'lecturer'
    ADMIN = 'admin'


# Database Configuration
host = "localhost"
user = "calvin2"
password = "12345678"
database = "database_final_project_v1"

# Database Connection
connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)


# User class for Flask-Login
class User():
    def __init__(self, user_id,fname, account_type):
        self.id = user_id
        self.account_type = account_type
        self.fname = fname
        # self.username = username
    def is_active(self):
    # Define logic to determine if the user is active.
        return True  # For simplicity, always return True for now.

    def is_authenticated(self):
        # Define logic to determine if the user is authenticated.
        return True  # For simplicity, always return True for now.

    def is_anonymous(self):
        # Define logic to determine if the user is anonymous.
        return False  # For simplicity, always return False for now.

    def get_id(self):
        # Return a unique identifier for the user.
        return str(self.id)
    def get_account_type(self):
        return self.account_type

@login_manager.user_loader
def load_user(user_id):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        user_id, fname, lname, account_type, password = user_data
        return User(user_id,fname,UserType(account_type))
    return None


@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        form = request.get_json()
        if form:
            username = form['username']
            password = form['password']

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user WHERE user_id = %s", (username,))
            user_data = cursor.fetchone()
            if user_data:
                user_id, fname, lname, account_type, hashed_password = user_data
                if username == str(user_id) and bcrypt.check_password_hash(hashed_password, password):
                    user = load_user(user_id)
                    login_user(user)
                    session['user_id'] = user_id
                    session['user_firstname'] = fname
                    session['account_type'] = account_type

                    user_data = {
                        "user_id": user_id,
                        "fname": fname,
                        "lname": lname,
                        "account_type": account_type

                    }
                    return jsonify({"message":"Login Successful", 'user': user_data}), 200
                else:
                    return jsonify({"message":"Invalid username or password"}), 400
            else:
                return jsonify({"message":"Invalid username or password"}), 400

    except:
        form= LoginForm()
        try:
            if session['account_type']:
                return redirect(url_for('home'))
        except:
            pass
        
        if request.method == 'POST' and form.validate_on_submit:
            username = request.form['username']
            password = request.form['password']

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user WHERE user_id = %s", (username,))
            user_data = cursor.fetchone()
            if user_data:
                user_id, fname, lname, account_type, hashed_password = user_data
                if username == str(user_id) and bcrypt.check_password_hash(hashed_password, password):
                    user = load_user(user_id)
                    login_user(user)
                    session['user_firstname'] = fname
                    session['account_type'] = account_type
                    
                    if current_user.is_authenticated:
                        return redirect(url_for("home"))
            else:
                flash('Invalid username or password', 'danger')
        return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


###
# Routing for your application.
###

@app.route('/')
def home():
    try: 
        """Render website's home page."""
        if session['account_type'] == UserType.STUDENT.value:
            return render_template('studentHome.html', user=current_user)
        elif session['account_type'] == UserType.LECTURER.value:
            return render_template('lecturerHome.html', user=current_user)
        elif session['account_type'] == UserType.ADMIN.value:
            return render_template('adminHome.html', user=current_user)
    except:
        pass
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    try:
        current_user = load_user(current_user.id)
        return render_template('about.html', user=current_user)
    except:
        # return render_template('about.html')
        pass
    # if current_user:
    #     return render_template('about.html', user=current_user)
    # else:

        
@login_required
@app.route('/add/courses', methods = ['POST','GET'])
def add_course():
    form = CourseForm()
    if request.method == 'POST':
        # Get the data from postman api request    
        if request.headers.get('Content-Type') == 'application/json':
            data = request.get_json()
            course_code = data['course_code']
            course_name = data['course_name']
            # Insert the course into the database
            cursor = connection.cursor()
            try:
                query = "INSERT INTO course (course_code, course_name) VALUES (%s, %s)"
                cursor.execute(query, (course_code, course_name))
                connection.commit()
                cursor.close()
                return jsonify({"message": "Course added successfully", 'course': data}), 200
            except:
                return jsonify({"message": "Course not added"}), 400
            
        if form.validate_on_submit():
            course_code = form.course_code.data
            course_name = form.course_name.data
            # Insert the course into the database
            cursor = connection.cursor()
            try: 
                query = "INSERT INTO course (course_code, course_name) VALUES (%s, %s)"
                cursor.execute(query, (course_code, course_name))
                connection.commit()
                cursor.close()
                flash('Course added successfully', 'success')
                form.course_code.data = ""
                form.course_name.data = ""
                return render_template('addCourse.html', form=form)
            except:
                flash('Course not added', 'danger')

    return render_template('addCourse.html', form=form)

def get_courses():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM course")
    courses = cursor.fetchall()
    cursor.close()
    return courses
# @login_required
@app.route('/courses', methods = ['GET'])
def view_courses():
    query = "SELECT * FROM course"
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    courses = []
    for course in result:
        courses.append({'course_code':course[0], 'course_name':course[1]})
    
    if courses:
        
        return render_template('courses.html', courses=courses)

@app.route('/courses/api', methods = ['GET'])
def view_courses_api():
    if request.method == 'GET':
        return jsonify({"courses":get_courses()})
    
@app.route('/courses/student/<student_id>')
def view_course_by_student(student_id):
    courses = []

    try:
        query = "SELECT registration.course_code, course_name FROM registration JOIN course ON registration.course_code = course.course_code where user_id = %s" 
        cursor = connection.cursor()
        cursor.execute( query, (student_id,))
        result = cursor.fetchall()
        cursor.close()
        for course in result:
            courses.append({'course_code':course[0], 'course_name':course[1]})
    except:
        pass
    return render_template('courses.html', courses=courses)

@app.route('/courses/student/api/<student_id>')
def view_course_by_student_api(student_id):
    try:
        query = "SELECT registration.course_code, course_name FROM registration JOIN course ON registration.course_code = course.course_code where user_id = %s" 
        cursor = connection.cursor()
        cursor.execute( query, (student_id,))
        result = cursor.fetchall()
        cursor.close()
        courses = []
        for course in result:
            courses.append({'course_code':course[0], 'course_name':course[1]})
        return jsonify({"courses":courses})
    except:
        pass

@app.route('/courses/lecturer/<user_id>')
def view_course_by_lecturer(user_id):
    try:
        query = "SELECT * FROM teaches where user_id = %s" 
        cursor = connection.cursor()
        cursor.execute( query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        courses = []
        for course in result:
            courses.append({'course_code':course[0], 'course_name':course[1]})
    except:
        pass
    return render_template('courses.html', courses=courses)

@app.route('/courses/lecturer/api/<user_id>')
def view_course_by_lecturer_api(user_id):
    try:
        query = "SELECT * FROM teaches where user_id = %s" 
        cursor = connection.cursor()
        cursor.execute( query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        courses = []
        for course in result:
            courses.append({'course_code':course[0], 'course_name':course[1]})
        return jsonify({"courses":courses})
    except:
        pass

@app.route('/admin/filter',methods = ['POST'])
def admin_filter():
    # if student_id in request.form:
    try:
        student_id = request.form['student_id']
        return redirect(url_for('view_course_by_student', student_id=student_id))
    except:
        pass
    try: 
    # elif lecturer_id in request.form:
        lecturer_id = request.form['lecturer_id']
        return redirect(url_for('view_course_by_lecturer', user_id=lecturer_id))
   
    except:
        pass
    
    # else:
    return redirect(url_for('view_courses'))
    
    
#adding a user
@login_required
@app.route('/add/user', methods = ['GET', 'POST'])
def add_user():
    try:
        form = request.get_json()
        if form:
            fname = form['fname']
            lname = form['lname']
            account_type = form['account_type']

            random_password = generate_random_password(7)
            #generate a password using bycrypt
            hashed_password = bcrypt.generate_password_hash(random_password).decode('utf-8')
            #query the user table for the student with the highest id
            try: 
                cursor = connection.cursor()
                cursor.execute("SELECT MAX(user_id) FROM user where account_type = %s", (account_type,))
                result = cursor.fetchone()
                
                result2 = cursor.execute(f"SELECT {account_type}_id FROM UserKey")
                result2 = cursor.fetchone()
            
                user_id = max(result[0], result2[0]) + 1
                cursor.execute(f"UPDATE UserKey SET { account_type}_id = %s", (user_id,))
                # connection.commit()
            except:
                return jsonify({"message":"User not added"})
                
            try:
                cursor.execute("INSERT INTO user VALUES (%s, %s, %s, %s, %s)", (user_id, fname, lname, account_type, hashed_password))
                connection.commit()
                cursor.close()

                user_data = {
                "user_id": user_id,
                "fname": fname,
                "lname": lname,
                "account_type": account_type,
                "password": random_password
                }    
                return jsonify ({"message":'User added successfully', "user":user_data})
            except:
                return jsonify({"message":"User not added"})
    except:
        try:
        
            if  session['account_type'] != UserType.ADMIN.value:
                return redirect(url_for('home'))
        except:
            return redirect(url_for('home'))
            # pass
        form = UserForm()
        if form.validate_on_submit():
            fname = form.fname.data
            lname = form.lname.data
            account_type = form.account_type.data

            random_password = generate_random_password(7)
            #generate a password using bycrypt
            hashed_password = bcrypt.generate_password_hash(random_password).decode('utf-8')
            #query the user table for the student with the highest id
            try: 
                cursor = connection.cursor()
                cursor.execute("SELECT MAX(user_id) FROM user where account_type = %s", (account_type,))
                result = cursor.fetchone()
                
                result2 = cursor.execute(f"SELECT {account_type}_id FROM UserKey")
                result2 = cursor.fetchone()
            
                user_id = max(result[0], result2[0]) + 1
                cursor.execute(f"UPDATE UserKey SET { account_type}_id = %s", (user_id,))
                # connection.commit()
            except:
                flash('User not added', 'danger')
                return render_template('addUser.html', form=form)
            try:
                cursor.execute("INSERT INTO user VALUES (%s, %s, %s, %s, %s)", (user_id, fname, lname, account_type, hashed_password))
                connection.commit()
                cursor.close()

                flash(f'User added successfully: user_id: {user_id}, password: {random_password}', 'success')
                form.fname.data = ''
                form.lname.data = ''
                
            except:
                flash('User not added', 'danger')
        return render_template('addUser.html', form=form)

# @login_required
# @app.route('/api/add/user', methods = ['GET', 'POST'])
# def add_user_api():
    
    












def generate_random_password(length=7):
    alphabet = string.ascii_letters + string.digits  # Include letters (both cases) and digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def get_uploaded_images():
    upload_folder = app.config['UPLOAD_FOLDER']
    uploaded_images = []

    if not os.path.exists(upload_folder):
        flash("File not found. Your uploads folder may have been removed")
    print(upload_folder)
    
    for filename in os.listdir(upload_folder):
        # Check if the path is a file (not a directory)
            if os.path.isfile(os.path.join(upload_folder, filename)):
                if filename.endswith(('.jpg', '.png')):
                    uploaded_images.append(filename)
    
    return uploaded_images


@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/files')
@login_required
def files():
    images_ = get_uploaded_images()
    return render_template('files.html', images=images_)






# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
