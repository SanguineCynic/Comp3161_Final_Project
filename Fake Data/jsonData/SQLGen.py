import json

# Open and read the JSON file
with open('C:/Users/jastw/Downloads/Database/Comp3161_Final_Project/Fake Data/jsonData/teaches.json', 'r') as file:
    json_data = json.load(file)

# Prepare the SQL INSERT statement
insert_statement = "INSERT INTO teaches (user_id, course_code) VALUES "

# Iterate through the items and append them to the INSERT statement
for item in json_data:
    insert_statement += f"('{item['user_id']}', '{item['course_code']}'), "

# Remove the trailing comma and space
insert_statement = insert_statement.rstrip(', ')

# Write the INSERT statement to a.sql file
with open('C:/Users/jastw/Downloads/Database/Comp3161_Final_Project/Fake Data/jsonData/student.sql', 'w') as file:
    file.write(insert_statement)

print("SQL file generated successfully.")
# {"user_id": 10034699, "course_code": "SWEN748"}