
from users import make_user
from course import make_course
from json_maker import save_json, load_json
import random

lecturer_list = load_json('users.json')
lecturer_list = [ lecturer for lecturer in lecturer_list if lecturer['type'] == 'lecturer' ]

course_list = load_json('course.json')

# print (f"The lengh of lecturer_list is: {len(lecturer_list)}")


# Assuming you have lists of user IDs and course IDs
user_ids = [user['user_id'] for user in lecturer_list if user['type'] == 'lecturer']
course_codes = [course['course_code'] for course in course_list]

print(f"The course code list is: {course_codes}")

# Create Teaches list
teaches = []

# Shuffle the lists to randomize the assignment
random.shuffle(user_ids)
random.shuffle(course_codes)

# Iterate over each user_id and assign courses to teach
for user_id in user_ids:
    # Randomly select the number of courses to teach (between 1 and 5 or the remaining courses) start with
    num_courses = min(random.randint(1, 4), len(course_codes))
    
    # Select courses to teach (up to num_courses)
    selected_courses = course_codes[:num_courses]
    

    # Update course_codes by removing the selected courses
    course_codes = course_codes[num_courses:]
    
    # Create teaches entry for each selected course
    for course_id in selected_courses:
        teaches.append({
            'user_id': user_id,
            'course_id': course_id
        })

# Print Teaches list
# for teach in teaches:
#     print(teach)



def check_course_occurrence(course_id, teaches):
    # Initialize count
    count = 0
    
    # Iterate over each entry in teaches
    for entry in teaches:
        # Check if the course_id matches the entry's course_id
        if entry['course_id'] == course_id:
            count += 1
    
    return count


json = save_json(teaches, 'teaches.json')
if  __name__ == "__main__":
    # Get unique course IDs to ensure that there are no repeats: 
    def check_unique_course_codes():
        unique_course_codes = set(entry['course_id'] for entry in teaches)

        # Iterate over each unique course ID and check its occurrence
        for course_id in unique_course_codes:
            occurrences = check_course_occurrence(course_id, teaches)
            print(f"{course_id}' occurs {occurrences} ")


    # check_unique_course_codes()

# print (len(teaches))