from course import make_course
from users import make_user
from json_maker import save_json, load_json
import random

# Load students from student.json
student_list = load_json('student.json')

# Load courses from course.json
course_list = load_json('course.json')

# Function to generate random final_average (0-99)
def generate_final_average():
    return random.randint(0, 99)

# Create registration list
registration = []

# Iterate over each student
for student in student_list:
    # Randomly select the number of courses (between 3 and 6)
    num_courses = random.randint(3, 6)
    
    # Ensure selected courses are unique
    selected_courses = random.sample(course_list, num_courses)
    
    # check for duplicates and remove them
    selected_courses = list({course['course_code']: course for course in selected_courses}.values())
    
    # Create registration entry for each selected course
    for course in selected_courses:
        registration.append({
            'user_id': student['user_id'],
            'course_code': course['course_code'],
            'final_average': generate_final_average()
        })
json = save_json(registration, 'registration.json')

if __name__ == "__main__":
    #Print all registrations
    for registration_entry in registration:
        print(registration_entry)

    def debug ():
        # Count registrations per user ID
        user_id_counts = {}
        for registration_entry in registration:
            user_id = registration_entry['user_id']
            if user_id in user_id_counts:
                user_id_counts[user_id] += 1
            else:
                user_id_counts[user_id] = 1

        # Print counts for each student registration 
        for user_id, count in user_id_counts.items():
            print(f"User ID: {user_id}, Registrations: {count}")
    debug()

  
    


