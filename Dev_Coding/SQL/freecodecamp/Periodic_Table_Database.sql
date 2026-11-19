-- Made by: Hazzard
-- FreeCodeCamp Relational Database Certification
-- Project: Periodic Table Database (PostgreSQL)
-- Final schema after the project's "fix the database" tasks.
-- Used by ../../Bash/freecodecamp/Periodic_Table_Element.sh

-- 1. Database
CREATE DATABASE periodic_table;
\c periodic_table

-- 2. Table Definitions
CREATE TABLE types (
    type_id SERIAL PRIMARY KEY,
    type    VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE elements (
    atomic_number INT PRIMARY KEY,
    symbol        VARCHAR(2)  NOT NULL UNIQUE,
    name          VARCHAR(40) NOT NULL UNIQUE
);

CREATE TABLE properties (
    atomic_number         INT PRIMARY KEY REFERENCES elements(atomic_number),
    type_id               INT NOT NULL REFERENCES types(type_id),
    atomic_mass           DECIMAL NOT NULL,
    melting_point_celsius DECIMAL NOT NULL,
    boiling_point_celsius DECIMAL NOT NULL
);

-- 3. Data
INSERT INTO types (type) VALUES ('metal'), ('nonmetal'), ('metalloid');

INSERT INTO elements (atomic_number, symbol, name) VALUES
(1, 'H', 'Hydrogen'), (2, 'He', 'Helium'), (3, 'Li', 'Lithium'),
(4, 'Be', 'Beryllium'), (5, 'B', 'Boron'), (6, 'C', 'Carbon'),
(7, 'N', 'Nitrogen'), (8, 'O', 'Oxygen'), (9, 'F', 'Fluorine'),
(10, 'Ne', 'Neon');

INSERT INTO properties (atomic_number, type_id, atomic_mass, melting_point_celsius, boiling_point_celsius) VALUES
(1, 2, 1.008, -259.1, -252.9),
(2, 2, 4.0026, -272.2, -269),
(3, 1, 6.94, 180.54, 1342),
(4, 1, 9.0122, 1287, 2470),
(5, 3, 10.81, 2075, 4000),
(6, 2, 12.011, 3550, 4027),
(7, 2, 14.007, -210.1, -195.8),
(8, 2, 15.999, -218, -183),
(9, 2, 18.998, -220, -188.1),
(10, 2, 20.18, -248.6, -246.1);

-- 4. Queries
-- Element card, as printed by the Bash script
SELECT
    elm.atomic_number,
    elm.name,
    elm.symbol,
    typ.type,
    prp.atomic_mass,
    prp.melting_point_celsius,
    prp.boiling_point_celsius
FROM elements AS elm
JOIN properties AS prp ON prp.atomic_number = elm.atomic_number
JOIN types AS typ      ON typ.type_id = prp.type_id
ORDER BY elm.atomic_number;

-- Count of elements per type
SELECT
    typ.type,
    COUNT(prp.atomic_number) AS element_count
FROM types AS typ
LEFT JOIN properties AS prp ON prp.type_id = typ.type_id
GROUP BY typ.type
ORDER BY element_count DESC;
