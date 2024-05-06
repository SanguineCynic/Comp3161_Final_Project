import mysql.connector

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