import mysql.connector

host = "localhost"
user = "calvin2"
password = "12345678"
database = "database_final_project_v1"

connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password
)

cursor = connection.cursor()
cursor.execute(f"DROP DATABASE IF EXISTS {database} ")
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
cursor.execute(f"USE {database};")
table_creation_queries = [
    """
    CREATE TABLE IF NOT EXISTS User (
        user_id INT PRIMARY KEY,
        fname VARCHAR(50) NOT NULL,
        lname VARCHAR(50) NOT NULL,
        account_type ENUM('student', 'lecturer', 'admin') NOT NULL,
        password VARCHAR(255) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Course (
        course_code VARCHAR(10) PRIMARY KEY,
        course_name VARCHAR(100) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Student (
        user_id INT PRIMARY KEY,
        earned_creds INT,
        gpa DECIMAL(3, 2),
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Registration (
        user_id INT,
        course_code VARCHAR(10),
        final_average DECIMAL(4, 2),
        PRIMARY KEY (user_id, course_code),
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (course_code) REFERENCES Course(course_code)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Teaches (
        user_id INT,
        course_code VARCHAR(10),
        PRIMARY KEY (user_id, course_code),
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (course_code) REFERENCES Course(course_code)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Section (
        section_id INT PRIMARY KEY AUTO_INCREMENT,
        course_code VARCHAR(10),
        title VARCHAR(100),
        description TEXT,
        FOREIGN KEY (course_code) REFERENCES Course(course_code)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Content (
        content_id INT PRIMARY KEY AUTO_INCREMENT,
        section_id INT,
        title VARCHAR(100),
        files_names JSON DEFAULT 'NONE',
        material TEXT DEFAULT 'NONE',
        FOREIGN KEY (section_id) REFERENCES Section(section_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS CalendarEvent (
        event_id INT PRIMARY KEY,
        section_id INT,
        title VARCHAR(100),
        file_names JSON,
        description TEXT,
        event_type VARCHAR(50),
        start_date DATETIME,
        end_date DATETIME,
        FOREIGN KEY (section_id) REFERENCES Section(section_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Submission (
        user_id INT,
        event_id INT,
        file_names JSON,
        text_content TEXT,
        grade DECIMAL(3, 2),
        PRIMARY KEY (user_id, event_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (event_id) REFERENCES CalendarEvent(event_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS DiscussionForum (
        forum_id INT PRIMARY KEY,
        course_id VARCHAR(10),
        title VARCHAR(100),
        description TEXT,
        FOREIGN KEY (course_id) REFERENCES Course(course_code)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS DiscussionThread (
        thread_id INT PRIMARY KEY,
        forum_id INT,
        user_id INT,
        title VARCHAR(100),
        content TEXT,
        FOREIGN KEY (forum_id) REFERENCES DiscussionForum(forum_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Reply (
        reply_id INT PRIMARY KEY,
        thread_id INT,
        user_id INT,
        parent_reply_id INT,
        message TEXT,
        FOREIGN KEY (thread_id) REFERENCES DiscussionThread(thread_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (parent_reply_id) REFERENCES Reply(reply_id)
    )
    """,
    """
    DROP TABLE IF EXISTS UserKey
    """,
    """
    CREATE TABLE IF NOT EXISTS UserKey (
        admin_id INT,
        lecturer_id INT,
        student_id INT
    )
    """,
    """
    INSERT INTO UserKey (admin_id, lecturer_id, student_id) VALUES (84630, 10034670, 620130490)
    
    """
]

# Execute each table creation query
for query in table_creation_queries:
    cursor.execute(query)
    # pass

connection.commit()
cursor.close()
connection.close()


def drop_tables(host, user, password):
    connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password
    )
    

    cursor = connection.cursor()
    cursor.execute(f"USE {database};")
    cursor.execute("""DROP TABLE IF EXISTS Reply""")
    cursor.execute("""DROP TABLE IF EXISTS DiscussionThread""")
    cursor.execute("""DROP TABLE IF EXISTS DiscussionForum""")
    cursor.execute("""DROP TABLE IF EXISTS Submission""")
    cursor.execute("""DROP TABLE IF EXISTS CalendarEvent""")
    cursor.execute("""DROP TABLE IF EXISTS Content""")
    cursor.execute("""DROP TABLE IF EXISTS Section""")
    cursor.execute("""DROP TABLE IF EXISTS Teaches""")
    cursor.execute("""DROP TABLE IF EXISTS Registration""")
    cursor.execute("""DROP TABLE IF EXISTS Student""")
    cursor.execute("""DROP TABLE IF EXISTS Course""")
    cursor.execute("""DROP TABLE IF EXISTS User""")

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    # uncomment if you want to drop all tables
    # drop_tables(host, user, password)
    pass



