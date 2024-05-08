from json_maker import save_json, load_json


import random

student_list = load_json('users.json')
student_list = [ student for student in student_list if student['type'] == 'student' ]
# Function to generate random earned_creds (0-120) and gpa (1-4)
def generate_random_values():
    return {
        'earned_creds': random.randint(0, 120),
        'gpa': round(random.uniform(1, 4), 2)
    }

# Create a new list of dictionaries with the required keys



if __name__ == '__main__':
    new_student_data = [{'user_id': student['user_id'], **generate_random_values()} for student in student_list]
    for student in new_student_data:
       print(student)
    print(new_student_data)
    save_json(new_student_data, 'student.json')


