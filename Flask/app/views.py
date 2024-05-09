#Standard libraries
import os, json, string, jwt
from datetime import datetime, timedelta
from enum import Enum

#Flask imports
from app import app, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.forms import LoginForm, UploadForm, CourseForm, UserForm, CourseRegistrationForm, MembershipForm
from flask import send_from_directory
from flask_login import logout_user
from flask_bcrypt import Bcrypt

#MySQL connection and related imports
import secrets
import mysql.connector


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


@login_required
@app.route('/register', methods=['POST', 'GET'])
def register():
    form = CourseRegistrationForm()
    if request.method == 'POST':
        # submission from postman
        if  not form.validate_on_submit():
            try:
                # check authorization
                token = request.headers.get('Authorization')
                if not token:
                    return jsonify({"message": "No token provided"}), 400
                try:
                    user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
                    if user_data['account_type'] == UserType.STUDENT.value or user_data['account_type'] == UserType.ADMIN.value:
                        pass
                    else:
                        return jsonify({"message": "Student/ admin authorization required"}), 400
                except:
                    return jsonify({"message": "Invalid token"}), 400

                form = request.get_json()
                course_code = form['course_code'].upper()
                user_id = form['user_id']
                # check if user exists
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if not result:
                    return jsonify({"message":"User does not exist"}), 400

                if user_data['account_type'] == UserType.STUDENT.value:
                    # ensure that the authorization is for that student
                    if str(user_id) != str(user_data['user_id']):
                        return jsonify({"message": "Student, you are not the owner of this account. You are not authorized to make this request"}), 400
                            

                # check if course exists
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM course WHERE course_code = %s", (course_code,))
                result = cursor.fetchone()
                if not result:
                    return jsonify({"message":"Course does not exist"}), 400
                
                # check if user is already registered
                cursor.execute("SELECT * FROM registration WHERE course_code = %s AND user_id = %s", (course_code, user_id))
                result = cursor.fetchone()
                
                if result:
                    return jsonify({"message":"You are already registered for this course"}), 400
                
                # check if user has already registered for 5 courses
                cursor.execute("SELECT * FROM registration WHERE user_id = %s", (user_id,))
                result = cursor.fetchall()
                if len(result) >= 5:
                    return jsonify({"message":"You have already registered for 5  courses"}), 400
                
                # register user for course
                cursor.execute("INSERT INTO registration ( user_id, course_code) VALUES (%s, %s)", (user_id, course_code))
                connection.commit()
                cursor.close()
                user = {
                    'message': 'User registered successfully',
                    'user_id': user_id,
                    'course_code': course_code
                }

                return jsonify(user), 200
            
            except:
                form = CourseRegistrationForm()
                # pass

        # submission from form   
        elif form.validate_on_submit():
            # user_id = form.user_id.data
            course_code = form.course_code.data.upper()
            try:
               cursor = connection.cursor()

               # check if course exists
               cursor.execute("SELECT * FROM course WHERE course_code = %s", (course_code,))
               result = cursor.fetchone()
               if not result:
                   flash("Course does not exist", 'danger')
                   return render_template('register.html', form=form)
               
               # check if user is already registered
               cursor.execute("SELECT * FROM registration WHERE course_code = %s AND user_id = %s", (course_code, session['user_id']))
               result = cursor.fetchone()
               if result:
                   print(result)
                   flash("You are already registered for this course", 'danger')
                   return render_template('register.html', form=form)
               
               # check if user has already registered for 5 courses
               cursor.execute("SELECT * FROM registration WHERE user_id = %s", (session['user_id'],))
               result = cursor.fetchall()
               if len(result) >= 5:
                   flash("You have already registered for 5  courses", 'danger')
                   return render_template('register.html', form=form)
            
               # register user
               cursor.execute("INSERT INTO registration (course_code, user_id) VALUES (%s, %s)", (course_code, session['user_id']))
               connection.commit()
               cursor.close()
               form.course_code.data = ''
               flash("Course Registered Successfully: " + course_code, 'success')
               return render_template('register.html', form=form)
            
            except:
                render_template('register.html', form=form)
    # user must be student or admin
    if session['account_type'] == UserType.STUDENT.value or session['account_type'] == UserType.ADMIN.value:
        pass
    else:
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/teach', methods=['POST', 'GET'])
def teach():
    form = CourseRegistrationForm()
    if form.validate_on_submit():
            # user_id = form.user_id.data
            
            course_code = form.course_code.data.upper()
            try:
               cursor = connection.cursor()

               # check if course exists
               cursor.execute("SELECT * FROM course WHERE course_code = %s", (course_code,))
               result = cursor.fetchone()
               if not result:
                   flash("Course does not exist", 'danger')
                   return render_template('teach.html', form=form)
               
               # check if the course is already been taught
               cursor.execute("SELECT * FROM teaches WHERE course_code = %s", (course_code, ))
               result = cursor.fetchall()
               if result:
                   print(result)
                   flash("This course is already been taught", 'danger')
                   return render_template('teach.html', form=form)
               
               # check if lecturer has already registered for 5 courses
               cursor.execute("SELECT * FROM teaches WHERE user_id = %s", (session['user_id'],))
               result = cursor.fetchall()
               if len(result) >= 5:
                   flash("You are already teaching for 5  courses", 'danger')
                   return render_template('teach.html', form=form)
            
               # register user
               cursor.execute("INSERT INTO teaches (course_code, user_id) VALUES (%s, %s)", (course_code, session['user_id']))
               connection.commit()
               cursor.close()
               form.course_code.data = ''
               flash("Course Registered Successfully: " + course_code, 'success')
               return render_template('teach.html', form=form)
            
            except:
                render_template('register.html', form=form)

    # submission from postman
    else:
        
        try:
            if request.method == 'POST':

                #extract data from json
                data = request.get_json()
                user_id = data['user_id']
                course_code = data['course_code'].upper()

                # check for authorization
                token = request.headers.get('Authorization')
                if not token:
                    return jsonify({"message": "No token provided"}), 400
                else:
                    try: 
                        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
                        if user_data['account_type'] == UserType.ADMIN.value or user_data['account_type'] == UserType.LECTURER.value:
                            if user_data['account_type'] == UserType.LECTURER.value:
                                # check to ensure that the user is authenticated
                                if user_data['user_id'] != user_id:
                                    return jsonify({"message": "You are not authorized to perform this action"}), 400
                                else:
                                    pass
                            pass
                        else:
                            return jsonify({"message": "There was an error retrieving token data"}), 400
                    except:
                        return jsonify({"There was an error assigning user to course"}), 400
                
                try:
                    cursor = connection.cursor()

                    # check if course exists
                    cursor.execute("SELECT * FROM course WHERE course_code = %s", (course_code,))
                    result = cursor.fetchone()
                    if not result:
                        return jsonify({"message": "Course does not exist"}), 400
                    
                    # check if the course is already been taught
                    cursor.execute("SELECT * FROM teaches WHERE course_code = %s", (course_code, ))
                    result = cursor.fetchall()
                    if result:
                        return jsonify({"message": "This course has already been taught"}), 400
                    
                    # check if lecturer has already registered for 5 courses
                    cursor.execute("SELECT * FROM teaches WHERE user_id = %s", (user_id,))
                    result = cursor.fetchall()
                    if len(result) >= 5:
                        return jsonify({"message": "You are already teaching for 5  courses"}), 400
                    
                    # register user
                    cursor.execute("INSERT INTO teaches (course_code, user_id) VALUES (%s, %s)", (course_code, user_id))
                    connection.commit()
                    cursor.close()
            
                    response = jsonify({"message": "Course Registered Successfully: ", "user_id": user_id ,"course_code": course_code})
                    return response, 200
                
                except:
                    return jsonify({"message": "Course Registration Failed"}), 400


                #########################################################################################
                
        except:
           return jsonify({"message": "Course Registration Failed"}), 400

   
    # user must be lecturer or admin
    if session['account_type'] == UserType.LECTURER.value or session['account_type'] == UserType.ADMIN.value:
        pass
    else:
        return redirect(url_for('home'))
    return render_template('teach.html', form=form)

def my_login_manager(username,password):
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

            expiration_delta = app.config.get('JWT_EXPIRATION_DELTA', timedelta(hours=1))
            expiration_time = datetime.utcnow() + expiration_delta

            user_data = {
                "user_id": str(user_id), 
                "fname": fname,
                "lname": lname,
                "account_type": account_type,
                'exp': expiration_time

            }

            token = jwt.encode( user_data, app.config['SECRET_KEY'], algorithm='HS256')
            reponse = {
                'token': token,
                'user': user_data
            }
            return reponse
        else:
            return False
    else:
        return False


    
@app.route('/login', methods=['POST', 'GET'])
def login():
    #this section is for postman
    try:
        form = request.get_json()
        if 'username' in form and 'password' in form:
            username = form['username']
            password = form['password']
            logged_in = my_login_manager(username, password)
            if logged_in:
                return logged_in, 200
            else:
                return jsonify({"message": "Invalid username or password"}), 400
        
        return jsonify({"message": "Missing username or password"}), 400
    
    #this section is for web
    except:
        form= LoginForm()
        # redirect to home page if already logged in
        try:
            if session['account_type']:
                return redirect(url_for('home'))
        except:
            pass
        
        if request.method == 'POST' and form.validate_on_submit:
            username = request.form['username']
            password = request.form['password']
            logged_in = my_login_manager(username, password)
            if logged_in:
                user_id = logged_in['user']['user_id']
                user = load_user(user_id)
                login_user(user)
                session['user_firstname'] = logged_in['user']['fname']
                session['account_type'] = logged_in['user']['account_type']
                session['user_id'] = logged_in['user']['user_id']

                flash('You are now logged in', 'success')
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
    # session.clear()
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
        # current_user = load_user(current_user.id)
        return render_template('about.html', user=session['user_id'])
    except:
        # return render_template('about.html')
        pass
    # if current_user:
    #     return render_template('about.html', user=current_user)
    # else:
    return render_template('about.html')

        
@login_required
@app.route('/add/courses', methods = ['POST','GET'])
def add_course():
    form = CourseForm()
    if request.method == 'POST':
        # Get the data from postman api request    
        if request.headers.get('Content-Type') == 'application/json' :
            data = request.get_json()

            # only admin can add course
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"message": "No token provided"}), 400
            try:
                user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
                if user_data['account_type'] != UserType.ADMIN.value:
                    return jsonify({"message": "Admin authorization required"}), 400
            except:
                return jsonify({"message": "Invalid token"}), 400
            course_code = data['course_code']
            course_name = data['course_name']

            # check if the course already exists
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM course WHERE course_code = %s", (course_code,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return jsonify({"message": "Course already exists"}), 400

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
    if session['account_type'] != UserType.ADMIN.value:
            return redirect(url_for('home'))
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
    user_ = {
        'user_id': "",
        'user_type': ""
    }
    for course in result:
        courses.append({'course_code':course[0], 'course_name':course[1]})

    return render_template('courses.html', courses=courses, user_=user_)

@app.route('/courses/api', methods = ['GET'])
def view_courses_api():
    if request.method == 'GET':
        courses = []
        for course in get_courses():
            courses.append({'course_code':course[0], 'course_name':course[1]})
        return jsonify(courses )
    
@app.route('/drop_course/<course_code>')
def drop_course(course_code):
    if 'account_type' not in session:
        return redirect(url_for('login'))
    
    cursor = connection.cursor()
    if session['account_type'] == UserType.LECTURER.value:
       
        try:
            query = "DELETE FROM teaches WHERE course_code = %s AND user_id = %s"
            cursor.execute(query, (course_code, session['user_id']))
            connection.commit()
            cursor.close()
            flash('Course dropped successfully', 'success')
            return redirect(url_for('view_course_by_lecturer', user_id=session['user_id']))
        except:
            flash('Course not dropped', 'danger')
            return redirect(url_for('view_course_by_lecturer', user_id=session['user_id']))
        
    if session['account_type'] == UserType.STUDENT.value:
        try:
            query = "DELETE FROM registration WHERE course_code = %s AND user_id = %s"
            cursor.execute(query, (course_code, session['user_id']))
            connection.commit()
            cursor.close()
            flash('Course dropped successfully', 'success')
            return redirect(url_for('view_course_by_student', student_id=session['user_id']))
        except:
            flash('Course not dropped', 'danger')
            return redirect(url_for('view_course_by_student', student_id=session['user_id']))
   
    
@app.route('/courses/student/<student_id>')
def view_course_by_student(student_id):
    
    if 'account_type' not in session:
        return redirect(url_for('login'))
    
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

    if session['account_type'] == UserType.STUDENT.value:
            return render_template('myCoursesStudent.html', courses=courses)
    
    return render_template('courses.html', courses=courses, user_={"user_id":student_id,'user_type':UserType.STUDENT.value})

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
        return jsonify(courses)
    except:
        pass

@app.route('/courses/lecturer/<user_id>')
def view_course_by_lecturer(user_id):
    if 'account_type' not in session:
        return redirect(url_for('login'))
    
    courses = []

    try:
        query = "SELECT teaches.course_code, course_name FROM teaches JOIN course ON teaches.course_code = course.course_code where user_id = %s" 
        cursor = connection.cursor()
        cursor.execute( query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        for course in result:
            courses.append({'course_code':course[0], 'course_name':course[1]})
    except:
        pass

    if session['account_type'] == UserType.LECTURER.value:
            return render_template('myCoursesLecturer.html', courses=courses)
    
    return render_template('courses.html', courses=courses, user_={"user_id":user_id,'user_type':UserType.LECTURER.value})

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
        return jsonify(courses)
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

            # account_type = must be student or lecturer or admin
            if account_type.lower() not in ['student', 'lecturer', 'admin']:
                return jsonify({"message":"Invalid account type"})

            random_password = generate_random_password(7)
            #generate a password using bycrypt
            hashed_password = bcrypt.generate_password_hash(random_password).decode('utf-8')
            #query the user table for the student with the highest id
            try: 
                ############ UPDATED ###############
                cursor = connection.cursor()
                cursor.execute("SELECT MAX(user_id) FROM user where account_type = %s", (account_type,))
                result = cursor.fetchone()
                
                result2 = cursor.execute(f"SELECT MAX({account_type}_id) FROM UserKey")
                result2 = cursor.fetchone()

                try:
                    user_id = max(int(result[0]), int(result2[0])) + 1
                except:
                    user_id = result2[0] + 1
                
                cursor.execute(f"UPDATE UserKey SET { account_type}_id = %s", (user_id,))
                connection.commit()
                ####################
                
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
            pass
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
                
                result2 = cursor.execute(f"SELECT MAX({account_type}_id) FROM UserKey")
                result2 = cursor.fetchone()

                try:
                    user_id = max(int(result[0]), int(result2[0])) + 1
                except:
                    user_id = result2[0] + 1
                
                cursor.execute(f"UPDATE UserKey SET { account_type}_id = %s", (user_id,))
                connection.commit()
            except:
                flash('User not added1', 'danger')
                return render_template('addUser.html', form=form)
            try:
                cursor.execute("INSERT INTO user VALUES (%s, %s, %s, %s, %s)", (user_id, fname, lname, account_type, hashed_password))
                connection.commit()
                cursor.close()

                flash(f'User added successfully: user_id: {user_id}, password: {random_password}', 'success')
                # form.fname.data = ''
                # form.lname.data = ''
                
            except Exception as e:
                print(e)
                flash('User not added2', 'danger')

        # restrict access to non-admin users
        if session['account_type'] != UserType.ADMIN.value:
            # return redirect(url_for('home'))
            pass
        return render_template('addUser.html', form=form)


# retrieve members of a course
@login_required
@app.route('/retrieve/members/<course_code>', methods = ['GET', 'POST']) 
def retrieve_members_by_course(course_code):
    try:
   
        #check if the course exists
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM course WHERE course_code = %s", (course_code,))
        result = cursor.fetchone()
        if not result:
            flash('Course does not exist', 'danger')
            return redirect(url_for('retrieve_members'))
        
        
        cursor = connection.cursor()
        cursor.execute("SELECT registration.user_id, user.fname, user.lname FROM registration \
                    JOIN user on registration.user_id  = user.user_id WHERE registration.course_code = %s", (course_code,))
        students = cursor.fetchall()

        cursor.execute("SELECT teaches.user_id, user.fname, user.lname FROM teaches \
                    JOIN user on teaches.user_id  = user.user_id WHERE teaches.course_code = %s", (course_code,))
        lecturers = cursor.fetchall()
        # print(students)
        
        if not students:
            students = []
        else:
            students = [dict(zip(['student_id', 'fname', 'lname'], student)) for student in students]
        if not lecturers:
            lecturers = []
        else:
            lecturers = [dict(zip(['student_id', 'fname', 'lname'], lecturer)) for lecturer in lecturers]
        
        cursor.close()
        form = MembershipForm()
        flash('Course retrieved successfully', 'success')
        if not lecturers and not students:
            flash('there are no members in this course', 'success')
        return render_template('retrieveMembers.html', students=students, lecturers=lecturers, course_code=course_code, form=form) 
    except:
        return render_template('retrieveMembers.html', students=students, lecturers=lecturers, course_code=course_code, form=form) 


@login_required
@app.route('/api/retrieve/members/<course_code>', methods = ['GET', 'POST']) 
def retrieve_members_by_course_api(course_code):
    # postman api request
    try:
        course_code = course_code.upper()

        #check if the course exists
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM course WHERE course_code = %s", (course_code,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"message": "Course does not exist"}), 400
        else:
            cursor = connection.cursor()
            cursor.execute("SELECT registration.user_id, user.fname, user.lname FROM registration \
                        JOIN user on registration.user_id  = user.user_id WHERE registration.course_code = %s", (course_code,))
            students = cursor.fetchall()

            cursor.execute("SELECT teaches.user_id, user.fname, user.lname FROM teaches \
                        JOIN user on teaches.user_id  = user.user_id WHERE teaches.course_code = %s", (course_code,))
            lecturers = cursor.fetchall()
            # print(students)
            
            if not students:
                students = []
            else:
                students = [dict(zip(['student_id', 'fname', 'lname'], student)) for student in students]
            if not lecturers:
                lecturers = []
            else:
                lecturers = [dict(zip(['student_id', 'fname', 'lname'], lecturer)) for lecturer in lecturers]
            
            cursor.close()
            return jsonify({"students": students, "lecturers": lecturers}), 200

    except:
        return jsonify({"message": "Invalid request"}), 400
        # pass

@login_required
@app.route('/retrieve/members', methods = ['GET', 'POST'])
def retrieve_members():
    # postman api request
    # if 'course_code' in request.json:
    #     course_code = request.json['course_code']

    # form submission
    form  = MembershipForm()
    if form.validate_on_submit():
        # flash('Course retrieved successfully', 'success')
        course_code = form.course_code.data
        return redirect(url_for('retrieve_members_by_course', course_code=course_code))
    students = []
    lecturers = []
    return render_template('retrieveMembers.html', students=students, lecturers=lecturers, course_code="", form=form)



@app.route('/courses/min/registration/50', methods=['GET'])
def courses_with_50_or_more_students():
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT c.course_code, c.course_name
        FROM Course c
        JOIN Registration r ON c.course_code = r.course_code
        GROUP BY c.course_code
        HAVING COUNT(r.user_id) >= 2
    """
    cursor.execute(query)
    courses_data = cursor.fetchall()
    cursor.close()
    return jsonify(courses_data)


# DISCUSSION FORUMS
@app.route('/forums', methods=['GET', 'POST'])
def manage_discussion_forums():
    cursor = connection.cursor()
    if request.method == 'GET':
        # Retrieve all forums
        cursor.execute("SELECT * FROM DiscussionForum")
        forums = cursor.fetchall()
        return jsonify(forums)
    elif request.method == 'POST':
        # Extract data from the request
        data = request.get_json()
        
        # Validate the data (add your validation logic here)
        # For simplicity, this example assumes all fields are required and valid
        name = data.get('name')
        description = data.get('description')
        course_code = data.get('course_code')

        cursor.execute("SELECT course_code from course")
        courses = cursor.fetchall()
        #Refine fetchall into simple list
        courses = [course[0] for course in courses]

        if not name or not description or not course_code:
            return jsonify({"error": "Name, description and course code are required"}), 400
        
        if course_code.upper() in courses:
            #calculate forumID
            cursor.execute("SELECT MAX(forum_id) from DiscussionForum")
            currentForum = cursor.fetchone()[0]
            if not currentForum:
                forum_id = 1
            else:
                forum_id = currentForum+1
            print(currentForum)

            cursor.execute("INSERT INTO DiscussionForum (forum_id, course_id, title, description) VALUES (%s,%s,%s,%s)",(forum_id,course_code.upper(),name,description))
            connection.commit()
            # Return the newly created forum
            cursor.execute("SELECT * FROM DiscussionForum WHERE title = %s", (name,))
            new_forum = cursor.fetchone()
            return jsonify(new_forum), 201
            return jsonify({"message":"Forum created successfully!"}), 200
        else:
            return jsonify({"error":"Course code not found"}), 404



        
        # Insert the new forum into the database
        cursor = connection.cursor()
        cursor.execute("INSERT INTO DiscussionForum (name, description) VALUES (%s, %s)", (name, description))
        connection.commit()
        
# this has not been tested
@login_required
@app.route('/course/<course_code>')
def view_selected_course(course_code):
    if session['account_type'] == UserType.STUDENT.value:
        return render_template('viewCourseStudent.html', courseCode=course_code)
    else:
        if 'account_type' not in session:
            return redirect(url_for('login'))
        
        sections = []

        try:
            query = "SELECT * FROM section WHERE course_code = %s" 
            cursor = connection.cursor()
            cursor.execute( query, (course_code,))
            result = cursor.fetchall()
            cursor.close()
            for section in result:
                sections.append({'section_id':section[0], 'course_code':section[1], 'title':section[2], 'description':section[3]})
        except:
            pass
        return render_template('viewCourse.html', sections=sections, courseCode=course_code)
    

@login_required
@app.route('/course/add_section/<course_code>', methods=['POST', 'GET'])
def add_course_section(course_code):
    if request.method == 'GET':
        if session.get('account_type') == UserType.STUDENT.value:
            return render_template('viewCourseStudent.html', courseCode=course_code)
        else:
            return render_template('addSection.html', courseCode=course_code) 
    elif request.method == 'POST':
        try:
            if request.is_json:
                form = request.get_json()
            else:
                form = request.form.to_dict()
                
            if 'title' in form and 'description' in form:
                title = form['title']
                description = form['description']
                cursor = connection.cursor()
                # Using parameterized query to prevent SQL injection
                cursor.execute("INSERT INTO section (course_code, title, description) VALUES (%s, %s, %s)", (course_code, title, description))
                connection.commit()
                cursor.close()
                # Render success template
                return render_template('addContent.html', flash="Section Added Successfully", courseCode=course_code)
        except Exception as e:
            print(e)  # Log the exception for debugging
            # Render error template
            return render_template('viewCourse.html', message="An error occurred while adding the section", courseCode=course_code), 500
    # Render default template for other cases
    return render_template('viewCourse.html', message="Invalid request method", courseCode=course_code), 400



def create_section(course_code, title, description):
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO section (course_code, title, description) VALUES ({course_code}, {title}, {description})")
    user_data = cursor.fetchone()
    if user_data:
        user_id, fname, lname, account_type, hashed_password = user_data
        if username == str(user_id) and bcrypt.check_password_hash(hashed_password, password):
            user = load_user(user_id)
            login_user(user)
            session['user_id'] = user_id
            session['user_firstname'] = fname
            session['account_type'] = account_type


    
    """
    try:
        form = request.get_json()
        if 'username' in form and 'password' in form:
            username = form['username']
            password = form['password']
            logged_in = my_login_manager(username, password)
            if logged_in:
                return logged_in, 200
            else:
                return jsonify({"message": "Invalid username or password"}), 400
        
        return jsonify({"message": "Missing username or password"}), 400
    
    #this section is for web
    except:
        form= LoginForm()
        # redirect to home page if already logged in
        try:
            if session['account_type']:
                return redirect(url_for('home'))
        except:
            pass
        
        if request.method == 'POST' and form.validate_on_submit:
            username = request.form['username']
            password = request.form['password']
            logged_in = my_login_manager(username, password)
            if logged_in:
                user_id = logged_in['user']['user_id']
                user = load_user(user_id)
                login_user(user)
                session['user_firstname'] = logged_in['user']['fname']
                session['account_type'] = logged_in['user']['account_type']
                session['user_id'] = logged_in['user']['user_id']

                flash('You are now logged in', 'success')
                return redirect(url_for("home"))
            else:
                flash('Invalid username or password', 'danger')
        return render_template("login.html", form=form)
        """





##########################################################
# Functions for general functionality (helper functions) #
##########################################################

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


@app.route('/course_container')
def course_container():
    return render_template('courseContainer.html', count=5, course_name = "<Course Name>")

