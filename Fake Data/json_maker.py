import json


# Function to save student_list as JSON file
def save_json(student_list, filename):
    filename = f"jsonData//{filename}"
    with open(filename, 'w') as file:
        json.dump(student_list, file)

# Function to load student_list from JSON file
def load_json(filename):
    filename = f"jsonData//{filename}"
    with open(filename, 'r') as file:
        return json.load(file)


