-- Made by: Hazzard
-- FreeCodeCamp Relational Database Certification
-- Project: Bike Rental Shop Database
-- Relational schema for bikes inventory, customers, and active/completed rentals

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE bikes (
    bike_id SERIAL PRIMARY KEY,
    type VARCHAR(30) NOT NULL,
    size INT NOT NULL,
    available BOOLEAN DEFAULT TRUE NOT NULL
);

CREATE TABLE rentals (
    rental_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id),
    bike_id INT NOT NULL REFERENCES bikes(bike_id),
    date_rented TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    date_returned TIMESTAMP
);

-- Seed Bike Fleet
INSERT INTO bikes (type, size, available) VALUES
('Mountain', 28, TRUE),
('Mountain', 27, TRUE),
('Road', 29, TRUE),
('Road', 27, TRUE),
('BMX', 20, TRUE),
('BMX', 19, TRUE),
('Cruiser', 26, TRUE),
('Cruiser', 24, TRUE);

-- Seed Sample Customers
INSERT INTO customers (phone, name) VALUES
('555-1234', 'Alice Johnson'),
('555-5678', 'Bob Smith');

-- Seed Sample Rental Record
INSERT INTO rentals (customer_id, bike_id, date_rented) VALUES
(1, 2, '2026-11-18 10:00:00');

UPDATE bikes SET available = FALSE WHERE bike_id = 2;

-- Query: List Available Inventory
SELECT bike_id, type, size || ' inch' AS frame_size 
FROM bikes 
WHERE available = TRUE 
ORDER BY bike_id;

-- Query: Active Outstanding Rentals
SELECT 
    r.rental_id,
    c.name AS customer,
    c.phone,
    b.type || ' (' || b.size || '")' AS bike_rented,
    r.date_rented
FROM rentals r
JOIN customers c ON r.customer_id = c.customer_id
JOIN bikes b ON r.bike_id = b.bike_id
WHERE r.date_returned IS NULL;
