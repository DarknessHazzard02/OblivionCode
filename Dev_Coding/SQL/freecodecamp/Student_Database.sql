-- Made by: Hazzard
-- FreeCodeCamp Relational Database Certification
-- Project: Student Database Part 1 & 2
-- Covers: Schema Design, Many-to-Many Relationships, Foreign Keys, Inner/Left/Right Joins

-- 1. Create Schema
CREATE TABLE majors (
    major_id SERIAL PRIMARY KEY,
    major VARCHAR(50) NOT NULL
);

CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course VARCHAR(100) NOT NULL
);

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    major_id INT REFERENCES majors(major_id),
    gpa NUMERIC(3, 2)
);

CREATE TABLE majors_courses (
    major_id INT NOT NULL REFERENCES majors(major_id),
    course_id INT NOT NULL REFERENCES courses(course_id),
    PRIMARY KEY (major_id, course_id)
);

-- 2. Populate Sample Data
INSERT INTO majors (major) VALUES 
('Computer Science'), 
('Data Science'), 
('Web Development');

INSERT INTO courses (course) VALUES 
('Database Systems'), 
('Algorithms & Data Structures'), 
('Machine Learning'), 
('Full Stack Web Engineering');

INSERT INTO majors_courses (major_id, course_id) VALUES 
(1, 1), (1, 2), (1, 4),
(2, 1), (2, 2), (2, 3),
(3, 1), (3, 4);

INSERT INTO students (first_name, last_name, major_id, gpa) VALUES 
('Elena', 'Reyes', 1, 3.85),
('Marcus', 'Vance', 2, 3.60),
('Sophia', 'Chen', 1, 3.92),
('Liam', 'Novak', 3, 3.40),
('Aria', 'Kim', NULL, 3.75);

-- 3. Query Exercises
-- List all students with their declared major (handling undeclared students with LEFT JOIN):
SELECT 
    s.student_id,
    s.first_name || ' ' || s.last_name AS full_name,
    COALESCE(m.major, 'Undeclared') AS major,
    s.gpa
FROM students s
LEFT JOIN majors m ON s.major_id = m.major_id
ORDER BY s.gpa DESC;

-- List all courses required for Computer Science:
SELECT c.course
FROM courses c
JOIN majors_courses mc ON c.course_id = mc.course_id
JOIN majors m ON mc.major_id = m.major_id
WHERE m.major = 'Computer Science'
ORDER BY c.course;

-- Aggregate average GPA by major:
SELECT 
    m.major,
    COUNT(s.student_id) AS enrolled_students,
    ROUND(AVG(s.gpa), 2) AS average_gpa
FROM majors m
JOIN students s ON m.major_id = s.major_id
GROUP BY m.major
HAVING AVG(s.gpa) >= 3.5;
