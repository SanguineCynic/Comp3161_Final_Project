
# from flask_wtf import FlaskForm, FileField, FileAllowed, FileRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField
from wtforms.validators import InputRequired, DataRequired, Length, EqualTo



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class UploadForm(FlaskForm):
    file = FileField('Upload File', validators=[FileRequired(), FileAllowed(['jpg', 'png'])])



    
# Define the CourseForm using WTForms

class CourseForm(FlaskForm):
    course_code = StringField('Course Code', validators=[InputRequired()])
    course_name = StringField('Course Name', validators=[InputRequired()])

# Define choices for the account type select field
ACCOUNT_TYPE_CHOICES = [('student', 'Student'), ('lecturer', 'Lecturer'), ('admin', 'Admin')]

class UserForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    account_type = SelectField('Account Type', choices=ACCOUNT_TYPE_CHOICES, validators=[DataRequired()])



class CourseRegistrationForm(FlaskForm):
    # user_id = StringField('Username', validators=[DataRequired()])
    course_code = StringField('', validators=[DataRequired()])
    submit = SubmitField('Register')

class MembershipForm(FlaskForm):
    course_code = StringField('', validators=[DataRequired()])
    submit = SubmitField('Register')