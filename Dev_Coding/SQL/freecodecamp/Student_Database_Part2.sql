-- Made by: Hazzard
-- FreeCodeCamp Relational Database Certification
-- Project: Learn SQL by Building a Student Database - Part 2
-- Advanced Queries: JOINs, subqueries, aggregation, sorting

-- Expected schema (from Part 1):
-- students(student_id, first_name, last_name, major_id, gpa)
-- majors(major_id, major)
-- courses(course_id, course)
-- majors_courses(major_id, course_id)

-- 1. Full INNER JOIN: All students with their major
SELECT
    s.first_name,
    s.last_name,
    m.major
FROM students s
INNER JOIN majors m ON s.major_id = m.major_id
ORDER BY s.last_name;

-- 2. LEFT JOIN: Include students with no declared major (undeclared)
SELECT
    s.first_name,
    s.last_name,
    COALESCE(m.major, 'Undeclared') AS major
FROM students s
LEFT JOIN majors m ON s.major_id = m.major_id
ORDER BY s.last_name;

-- 3. RIGHT JOIN: Show all majors even if no students enrolled
SELECT
    COALESCE(s.first_name, 'No student') AS student,
    m.major
FROM students s
RIGHT JOIN majors m ON s.major_id = m.major_id
ORDER BY m.major;

-- 4. FULL OUTER JOIN: Every student AND every major regardless of association
SELECT
    s.first_name,
    s.last_name,
    m.major
FROM students s
FULL OUTER JOIN majors m ON s.major_id = m.major_id;

-- 5. Subquery: Students whose GPA is above the class average
SELECT first_name, last_name, gpa
FROM students
WHERE gpa > (SELECT AVG(gpa) FROM students)
ORDER BY gpa DESC;

-- 6. Aggregation: Student count and average GPA by major
SELECT
    m.major,
    COUNT(s.student_id) AS total_students,
    ROUND(AVG(s.gpa), 2) AS avg_gpa,
    MIN(s.gpa) AS lowest_gpa,
    MAX(s.gpa) AS highest_gpa
FROM majors m
LEFT JOIN students s ON m.major_id = s.major_id
GROUP BY m.major
ORDER BY avg_gpa DESC;

-- 7. Courses taken by more than one major
SELECT
    c.course,
    COUNT(mc.major_id) AS taken_by_majors
FROM courses c
JOIN majors_courses mc ON c.course_id = mc.course_id
GROUP BY c.course
HAVING COUNT(mc.major_id) > 1
ORDER BY taken_by_majors DESC;

-- 8. USING clause shorthand (when column names match)
SELECT s.first_name, m.major
FROM students s
JOIN majors m USING (major_id)
WHERE s.gpa >= 3.8;

-- 9. Pattern matching with ILIKE
SELECT first_name, last_name, gpa
FROM students
WHERE first_name ILIKE 'e%'
ORDER BY first_name;

-- 10. NULL handling: students without a major
SELECT first_name, last_name
FROM students
WHERE major_id IS NULL;
