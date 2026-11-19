-- Made by: Hazzard
-- FreeCodeCamp Relational Database Certification
-- Project: Learn Git by Building an SQL Reference Object
-- A self-documenting SQL reference table covering core SQL commands with examples

CREATE TABLE sql_reference (
    command_id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    command_name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    example_syntax TEXT NOT NULL
);

-- DML: Data Manipulation Language
INSERT INTO sql_reference (category, command_name, description, example_syntax) VALUES
('DML', 'SELECT',  'Retrieves rows from one or more tables',                    'SELECT col1, col2 FROM table_name WHERE condition;'),
('DML', 'INSERT',  'Adds new rows into a table',                                'INSERT INTO table_name (col1, col2) VALUES (val1, val2);'),
('DML', 'UPDATE',  'Modifies existing rows in a table',                         'UPDATE table_name SET col1 = val1 WHERE condition;'),
('DML', 'DELETE',  'Removes rows from a table',                                 'DELETE FROM table_name WHERE condition;');

-- DDL: Data Definition Language
INSERT INTO sql_reference (category, command_name, description, example_syntax) VALUES
('DDL', 'CREATE TABLE',   'Creates a new table in the database',                'CREATE TABLE table_name (col1 TYPE CONSTRAINT, col2 TYPE);'),
('DDL', 'ALTER TABLE',    'Modifies structure of an existing table',            'ALTER TABLE table_name ADD COLUMN col_name TYPE;'),
('DDL', 'DROP TABLE',     'Permanently removes a table',                        'DROP TABLE table_name;'),
('DDL', 'TRUNCATE',       'Removes all rows but keeps the table structure',     'TRUNCATE TABLE table_name;');

-- Joins
INSERT INTO sql_reference (category, command_name, description, example_syntax) VALUES
('JOIN', 'INNER JOIN',    'Returns rows that match in both tables',             'SELECT * FROM a INNER JOIN b ON a.id = b.a_id;'),
('JOIN', 'LEFT JOIN',     'Returns all rows from left and matched from right',  'SELECT * FROM a LEFT JOIN b ON a.id = b.a_id;'),
('JOIN', 'RIGHT JOIN',    'Returns all rows from right and matched from left',  'SELECT * FROM a RIGHT JOIN b ON a.id = b.a_id;'),
('JOIN', 'FULL JOIN',     'Returns all rows from both tables',                  'SELECT * FROM a FULL OUTER JOIN b ON a.id = b.a_id;');

-- Aggregates
INSERT INTO sql_reference (category, command_name, description, example_syntax) VALUES
('AGGREGATE', 'COUNT',   'Counts the number of rows',                          'SELECT COUNT(*) FROM table_name;'),
('AGGREGATE', 'SUM',     'Returns the sum of a numeric column',                'SELECT SUM(salary) FROM employees;'),
('AGGREGATE', 'AVG',     'Returns the average value of a numeric column',      'SELECT AVG(gpa) FROM students;'),
('AGGREGATE', 'MAX',     'Returns the maximum value of a column',              'SELECT MAX(score) FROM exams;'),
('AGGREGATE', 'MIN',     'Returns the minimum value of a column',              'SELECT MIN(price) FROM products;'),
('AGGREGATE', 'GROUP BY','Groups rows sharing a property for aggregation',     'SELECT dept, COUNT(*) FROM emp GROUP BY dept;'),
('AGGREGATE', 'HAVING',  'Filters groups after GROUP BY aggregation',          'SELECT dept, COUNT(*) FROM emp GROUP BY dept HAVING COUNT(*) > 5;');

-- Constraints
INSERT INTO sql_reference (category, command_name, description, example_syntax) VALUES
('CONSTRAINT', 'PRIMARY KEY',   'Uniquely identifies each row in a table',     'col_name INT PRIMARY KEY'),
('CONSTRAINT', 'FOREIGN KEY',   'Links a column to a primary key in another',  'FOREIGN KEY (col) REFERENCES other_table(col)'),
('CONSTRAINT', 'UNIQUE',        'Ensures no duplicate values in a column',     'email VARCHAR(100) UNIQUE'),
('CONSTRAINT', 'NOT NULL',      'Prevents null values in a column',            'name VARCHAR(50) NOT NULL'),
('CONSTRAINT', 'DEFAULT',       'Sets a default value if none provided',       'is_active BOOLEAN DEFAULT TRUE'),
('CONSTRAINT', 'CHECK',         'Validates data against a boolean expression', 'CHECK (gpa >= 0 AND gpa <= 4.0)');

-- Subqueries & Filtering
INSERT INTO sql_reference (category, command_name, description, example_syntax) VALUES
('FILTER', 'WHERE',      'Filters rows based on a condition',                  'SELECT * FROM table WHERE col > value;'),
('FILTER', 'BETWEEN',    'Checks if a value is in an inclusive range',         'WHERE salary BETWEEN 3000 AND 7000'),
('FILTER', 'IN',         'Matches any value in a provided list',               'WHERE country IN (''USA'', ''Canada'', ''Mexico'')'),
('FILTER', 'LIKE',       'Pattern matching with wildcards (% and _)',          'WHERE name LIKE ''A%'''),
('FILTER', 'IS NULL',    'Checks if a value is NULL',                          'WHERE major_id IS NULL'),
('FILTER', 'SUBQUERY',   'A query nested inside another query',                'WHERE salary > (SELECT AVG(salary) FROM employees)');

-- Reference Viewer
SELECT
    category,
    command_name,
    description,
    example_syntax
FROM sql_reference
ORDER BY category, command_id;
