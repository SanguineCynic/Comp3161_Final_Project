DROP DATABASE IF EXISTS database_final_project_v1;
CREATE DATABASE database_final_project_v1;
USE database_final_project_v1;

CREATE TABLE User (
    user_id INT PRIMARY KEY,
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    account_type ENUM('student', 'lecturer', 'admin') NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Course (
    course_code VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL
);

CREATE TABLE Student (
    user_id INT PRIMARY KEY,
    earned_creds INT,
    gpa DECIMAL(3, 2),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Registration (
    user_id INT,
    course_code VARCHAR(10),
    final_average DECIMAL(4, 2),
    PRIMARY KEY (user_id, course_code),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (course_code) REFERENCES Course(course_code)
);

CREATE TABLE Teaches (
    user_id INT,
    course_code VARCHAR(10),
    PRIMARY KEY (user_id, course_code),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (course_code) REFERENCES Course(course_code)
);

CREATE TABLE Section (
    section_id INT PRIMARY KEY,
    course_code VARCHAR(10),
    title VARCHAR(100),
    description TEXT,
    FOREIGN KEY (course_code) REFERENCES Course(course_code)
);

CREATE TABLE Content (
    content_id INT PRIMARY KEY,
    section_id INT,
    title VARCHAR(100),
    files_names JSON,
    material TEXT,
    FOREIGN KEY (section_id) REFERENCES Section(section_id)
);

CREATE TABLE CalendarEvent (
    event_id INT PRIMARY KEY,
    section_id INT,
    title VARCHAR(100),
    file_names JSON,
    description TEXT,
    event_type VARCHAR(50),
    start_date DATETIME,
    end_date DATETIME,
    FOREIGN KEY (section_id) REFERENCES Section(section_id)
);

CREATE TABLE Submission (
    user_id INT,
    event_id INT,
    file_names JSON,
    text_content TEXT,
    grade DECIMAL(3, 2),
    PRIMARY KEY (user_id, event_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (event_id) REFERENCES CalendarEvent(event_id)
);

CREATE TABLE DiscussionForum (
    forum_id INT PRIMARY KEY,
    course_id VARCHAR(10),
    title VARCHAR(100),
    description TEXT,
    FOREIGN KEY (course_id) REFERENCES Course(course_code)
);

CREATE TABLE DiscussionThread (
    thread_id INT PRIMARY KEY,
    forum_id INT,
    user_id INT,
    title VARCHAR(100),
    content TEXT,
    FOREIGN KEY (forum_id) REFERENCES DiscussionForum(forum_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE Reply (
    reply_id INT PRIMARY KEY,
    thread_id INT,
    user_id INT,
    parent_reply_id INT,
    message TEXT,
    FOREIGN KEY (thread_id) REFERENCES DiscussionThread(thread_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (parent_reply_id) REFERENCES Reply(reply_id)
);

CREATE TABLE UserKey (
    admin_id INT,
    lecturer_id INT,
    student_id INT,
    PRIMARY KEY (admin_id, lecturer_id, student_id)
);
