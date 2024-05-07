import mysql.connector
from json_maker import save_json, load_json
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

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


# insert users
def insert_users():
    cursor = connection.cursor()
    users_data = load_json('users.json')
    for user_data in users_data:
        # use bycrypt to encrypt 
        hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        user_data['password'] = hashed_password
        # Use parameterized query to insert data
        user_query = "INSERT INTO user (user_id, fname, lname, account_type, password) VALUES (%s, %s, %s, %s, %s)"
        user_values = (user_data['user_id'], user_data['fname'], user_data['lname'], user_data['type'], user_data['password'])
        cursor.execute(user_query, user_values)
    connection.commit()
    cursor.close()

# insert courses
def insert_courses():
    cursor = connection.cursor()
    courses_data = load_json('course.json')
    for course_data in courses_data:
        # Use parameterized query to insert data
        query = "INSERT INTO course (course_code, course_name) VALUES (%s, %s)"
        values = (course_data['course_code'], course_data['course_name'])
        cursor.execute(query, values)
    connection.commit()
    cursor.close()

# insert students
def insert_students():
    cursor = connection.cursor()
    students_data = load_json('student.json')
    for student_data in students_data:
        # Use parameterized query to insert data
        user_query = "INSERT INTO student (user_id, earned_creds, gpa) VALUES (%s, %s, %s)"
        user_values = (student_data['user_id'], student_data['earned_creds'], student_data['gpa'])
        cursor.execute(user_query, user_values)
    connection.commit()
    cursor.close()

# insert registrations
def insert_registrations():
    cursor = connection.cursor()
    registrations_data = load_json('registration.json')
    for registration_data in registrations_data:
        # Use parameterized query to insert data
        user_query = "INSERT INTO registration (user_id, course_code, final_average) VALUES (%s, %s, %s)"
        user_values = (registration_data['user_id'], registration_data['course_code'], registration_data['final_average'])
        cursor.execute(user_query, user_values)
    connection.commit()
    cursor.close()

# insert teaches
def insert_teaches():
    cursor = connection.cursor()
    teaches_data = load_json('teaches.json')
    for teach_data in teaches_data:
        # Use parameterized query to insert data
        user_query = "INSERT INTO teaches (user_id, course_code) VALUES (%s, %s)"
        user_values = (teach_data['user_id'], teach_data['course_code'])
        cursor.execute(user_query, user_values)
    connection.commit()
    cursor.close()

def save_user_SQL():
    users = load_json('users.json')
    final_query = "INSERT INTO User ( user_id, fname, lname, account_type, password) VALUES (\n"
    for user in users:
        insert_str = f"({user['user_id']}, '{user['fname']}', '{user['lname']}', '{user['type']}', '{user['password']}'),\n"
        final_query += insert_str
    final_query = final_query[:-2]
    final_query+= ";"
    print(final_query)


def clear_users():
    cursor = connection.cursor()
    cursor.execute("DELETE FROM User")
    connection.commit()
    cursor.close()
    




def select_all(table_name):
    cursor = connection.cursor()
    run_ = f"SELECT * FROM {table_name}"
    cursor.execute(run_)
    users = cursor.fetchall()
    print(users)
    cursor.close()
    connection.close()
    return users





if __name__ == "__main__":
    """ Insert data into database """
    # insert_users()
    # insert_courses()
    # insert_students()
    # insert_registrations()
    insert_teaches()

    """ Save data into sql file"""
    # save_user_SQL()
   
    """ Select data from database"""
    # select_all('user')
    



        



