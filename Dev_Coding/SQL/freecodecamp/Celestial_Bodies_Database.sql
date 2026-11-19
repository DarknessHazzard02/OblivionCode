-- FreeCodeCamp Relational Database Certification
-- Project: Celestial Bodies Database
-- Features: Foreign key relations, constraints, diverse data types, sample data

-- 1. Create Tables
CREATE TABLE galaxy (
    galaxy_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    galaxy_type VARCHAR(30) NOT NULL,
    age_in_millions_of_years INT,
    distance_from_earth NUMERIC(8, 2),
    has_supermassive_black_hole BOOLEAN NOT NULL
);

CREATE TABLE star (
    star_id SERIAL PRIMARY KEY,
    galaxy_id INT NOT NULL REFERENCES galaxy(galaxy_id) ON DELETE CASCADE,
    name VARCHAR(50) UNIQUE NOT NULL,
    spectral_type VARCHAR(10) NOT NULL,
    mass_in_solar_masses NUMERIC(6, 2),
    is_spherical BOOLEAN NOT NULL
);

CREATE TABLE planet (
    planet_id SERIAL PRIMARY KEY,
    star_id INT NOT NULL REFERENCES star(star_id) ON DELETE CASCADE,
    name VARCHAR(50) UNIQUE NOT NULL,
    planet_type VARCHAR(30) NOT NULL,
    has_life BOOLEAN NOT NULL,
    orbital_period_days NUMERIC(9, 2),
    number_of_moons INT DEFAULT 0
);

CREATE TABLE moon (
    moon_id SERIAL PRIMARY KEY,
    planet_id INT NOT NULL REFERENCES planet(planet_id) ON DELETE CASCADE,
    name VARCHAR(50) UNIQUE NOT NULL,
    radius_km INT NOT NULL,
    is_tidally_locked BOOLEAN NOT NULL
);

CREATE TABLE mission (
    mission_id SERIAL PRIMARY KEY,
    planet_id INT REFERENCES planet(planet_id),
    name VARCHAR(60) UNIQUE NOT NULL,
    launch_year INT NOT NULL,
    is_active BOOLEAN NOT NULL
);

-- 2. Insert Galaxies
INSERT INTO galaxy (name, galaxy_type, age_in_millions_of_years, distance_from_earth, has_supermassive_black_hole) VALUES
('Milky Way', 'Barred Spiral', 13610, 0.00, TRUE),
('Andromeda', 'Spiral', 10000, 2.54, TRUE),
('Triangulum', 'Spiral', 12000, 2.73, FALSE),
('Large Magellanic Cloud', 'Magellanic Spiral', 1101, 0.16, FALSE),
('Small Magellanic Cloud', 'Dwarf Irregular', 6500, 0.20, FALSE),
('Sombrero', 'Lenticular', 9000, 29.35, TRUE);

-- 3. Insert Stars
INSERT INTO star (galaxy_id, name, spectral_type, mass_in_solar_masses, is_spherical) VALUES
(1, 'Sun', 'G2V', 1.00, TRUE),
(1, 'Proxima Centauri', 'M5.5Ve', 0.12, TRUE),
(1, 'Betelgeuse', 'M1-2', 16.50, TRUE),
(1, 'Sirius', 'A1V', 2.06, TRUE),
(2, 'Alpheratz', 'B8IV', 3.80, TRUE),
(3, 'Triangulum Alpha', 'F6IV', 1.50, TRUE);

-- 4. Insert Planets
INSERT INTO planet (star_id, name, planet_type, has_life, orbital_period_days, number_of_moons) VALUES
(1, 'Mercury', 'Terrestrial', FALSE, 87.97, 0),
(1, 'Venus', 'Terrestrial', FALSE, 224.70, 0),
(1, 'Earth', 'Terrestrial', TRUE, 365.26, 1),
(1, 'Mars', 'Terrestrial', FALSE, 686.98, 2),
(1, 'Jupiter', 'Gas Giant', FALSE, 4332.59, 95),
(1, 'Saturn', 'Gas Giant', FALSE, 10759.22, 146),
(1, 'Uranus', 'Ice Giant', FALSE, 30685.40, 28),
(1, 'Neptune', 'Ice Giant', FALSE, 60189.00, 16),
(2, 'Proxima b', 'Super Earth', FALSE, 11.19, 0),
(2, 'Proxima c', 'Sub Neptune', FALSE, 1928.00, 0),
(2, 'Proxima d', 'Sub Earth', FALSE, 5.12, 0),
(5, 'Mirach Companion b', 'Gas Giant', FALSE, 580.00, 0);

-- 5. Insert Moons
INSERT INTO moon (planet_id, name, radius_km, is_tidally_locked) VALUES
(3, 'Moon', 1737, TRUE),
(4, 'Phobos', 11, TRUE),
(4, 'Deimos', 6, TRUE),
(5, 'Io', 1821, TRUE),
(5, 'Europa', 1560, TRUE),
(5, 'Ganymede', 2634, TRUE),
(5, 'Callisto', 2410, TRUE),
(6, 'Titan', 2574, TRUE),
(6, 'Enceladus', 252, TRUE),
(6, 'Mimas', 198, TRUE),
(6, 'Iapetus', 734, TRUE),
(6, 'Rhea', 763, TRUE),
(7, 'Titania', 788, TRUE),
(7, 'Oberon', 761, TRUE),
(7, 'Umbriel', 584, TRUE),
(7, 'Ariel', 578, TRUE),
(7, 'Miranda', 235, TRUE),
(8, 'Triton', 1353, TRUE),
(8, 'Proteus', 210, FALSE),
(8, 'Nereid', 170, FALSE);

-- 6. Insert Missions
INSERT INTO mission (planet_id, name, launch_year, is_active) VALUES
(3, 'Apollo 11', 1969, FALSE),
(4, 'Perseverance Rover', 2020, TRUE),
(5, 'Juno', 2011, TRUE);

-- Verification Query
SELECT 
    g.name AS galaxy,
    s.name AS star,
    p.name AS planet,
    COUNT(m.moon_id) AS total_moons
FROM galaxy g
JOIN star s ON g.galaxy_id = s.galaxy_id
JOIN planet p ON s.star_id = p.star_id
LEFT JOIN moon m ON p.planet_id = m.planet_id
GROUP BY g.name, s.name, p.name
ORDER BY total_moons DESC;
