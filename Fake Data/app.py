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

cursor = connection.cursor()
# select all resistration
cursor.execute( "SELECT * FROM registration" )
result = cursor.fetchall()
print(result)

# load user into db

users = load_json('users.json')

for user in users:
    user_query = "INSERT INTO user (user_id, fname, lname, account_type, password) VALUES (%s, %s, %s, %s, %s)"
    user_values = (user['user_id'], user['fname'], user['lname'], user['type'], user['password'])
    cursor.execute(user_query, user_values)
    connection.commit()