-- FreeCodeCamp Relational Database Certification
-- Project: Salon Appointment Scheduler
-- Schema and interactive relational model for customers, salon services, and appointment bookings

-- 1. Create Tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    price NUMERIC(5, 2) NOT NULL
);

CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    service_id INT NOT NULL REFERENCES services(service_id) ON DELETE CASCADE,
    time VARCHAR(20) NOT NULL
);

-- 2. Seed Services Catalog
INSERT INTO services (name, price) VALUES
('Cut', 30.00),
('Color', 75.00),
('Perm', 90.00),
('Style', 45.00),
('Trim', 20.00);

-- 3. Seed Sample Customers
INSERT INTO customers (phone, name) VALUES
('555-0101', 'Fabio'),
('555-0102', 'Diana'),
('555-0103', 'Carlos');

-- 4. Seed Appointments
INSERT INTO appointments (customer_id, service_id, time) VALUES
(1, 1, '10:30am'),
(2, 2, '01:00pm'),
(3, 4, '03:15pm');

-- 5. Daily Schedule Query
SELECT 
    a.time AS scheduled_time,
    c.name AS customer_name,
    c.phone AS customer_phone,
    s.name AS service_requested,
    s.price AS service_price
FROM appointments a
JOIN customers c ON a.customer_id = c.customer_id
JOIN services s ON a.service_id = s.service_id
ORDER BY a.appointment_id;
