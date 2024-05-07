import mysql.connector

import os, json, string, jwt
from datetime import datetime, timedelta
from enum import Enum

#Flask imports
from . import app
from app import  login_manager
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



def login_manager(username,password):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (username,))
    user_data = cursor.fetchone()
    if user_data:
        user_id, fname, lname, account_type, hashed_password = user_data
        if username == str(user_id): # and bcrypt.check_password_hash(hashed_password, password):
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


 