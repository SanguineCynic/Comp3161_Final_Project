# connection to database
import mysql.connector
from json_maker import save_json, load_json

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
    insert_courses()

    """ Save data into sql file"""
    # save_user_SQL()
   
    """ Select data from database"""
    # select_all('user')
    



        



