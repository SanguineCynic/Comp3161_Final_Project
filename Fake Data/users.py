import secrets
import string
from faker import Faker
from json_maker import save_json, load_json

# Create a Faker instance
fake = Faker()

# Number of persons you want to generate adjust as needed

user_index = ['lecturer', 'student', 'admin']

persons = []

def make_user (amount = [0]*len(user_index), type_= user_index, counter = 0):
    if counter == 3: # number of users from user_index for the system
        return persons
    else:
        # Starting user ID
        if type_[0] == 'lecturer':
            start_user_id = 10034670
        elif type_[0]  == 'student':
            start_user_id = 620130490
        elif type_[0]  == 'admin':
            start_user_id = 84630
        else:
            #exit with error message
            exit('Error: Type must be "lecturer", "student", or "admin"')
         
        # Function to generate random passwords with no special characters
        def generate_password():

            password_length = secrets.choice(range(7, 8))  # Random password length between 8 and 15 characters
            characters = string.ascii_letters + string.digits
            return ''.join(secrets.choice(characters) for _ in range(password_length))

        # Generate a list of persons with first and last names, type, user ID, and password
        persons.extend([{'user_id': start_user_id + i,
                    'fname': fake.first_name(), 
                    'lname': fake.last_name(),
                    'type': type_[0],
                    'password': generate_password()} 
                for i in range(amount[0])])
        return make_user(amount[1:], type_[1:], counter + 1)





lecturer_amount,students_amount, admin_amount = 40,1500,2
amount_index = [lecturer_amount, students_amount, admin_amount]
make_user(amount=amount_index)
save_json(persons, 'users.json')


    

        
if __name__ == '__main__':
    # Call the function
    # runAll()
    pass




