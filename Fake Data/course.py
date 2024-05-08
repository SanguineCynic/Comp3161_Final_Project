import random
from json_maker import save_json, load_json

def make_course(amount):
    course_list = []  # Initialize an empty list to store courses

    # Define course subject areas
    subjects = ["SWEN", "MATH", "PHYS", "BIOL", "HIST", "ENGL", "ECON", "PSYC", "COMP", "MGMT", "LANG"]

    # Generate 300 courses
    for i in range(300):
        # Generate random course code
        course_code = random.choice(subjects) + str(random.randint(100, 999))[:3]

        # Generate random course title
        course_title = f"Course Name {course_code}"

        # Add course to list
        this_course = {'course_code': course_code, 'course_name': course_title}
        if this_course not in course_list:
            course_list.append(this_course)
        

        # Exit loop if we have reached 210 courses
        set_check = set()
        for course in course_list:
            set_check.add(course['course_code'])

        if len(set_check) >= amount: 
            break
    
    return course_list

if __name__ == "__main__":
    # for course in make_course(10):
    #     print(course)

    # add the number of courses
    num_courses = 200
    save_json(make_course(num_courses), 'course.json')