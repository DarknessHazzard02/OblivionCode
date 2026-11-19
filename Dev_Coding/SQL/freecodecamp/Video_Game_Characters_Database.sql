-- Made by: Hazzard
-- FreeCodeCamp: Learn Relational Databases by Building a Database of
-- Video Game Characters (PostgreSQL)
-- Teaches: CREATE/ALTER, primary and foreign keys, one-to-one,
-- one-to-many and many-to-many relationships, joins.
-- Characters below are original, invented for this exercise.

-- 1. Database
CREATE DATABASE game_characters;
\c game_characters

-- 2. Table Definitions
CREATE TABLE characters (
    character_id   SERIAL PRIMARY KEY,
    name           VARCHAR(30) NOT NULL,
    homeland       VARCHAR(60),
    favorite_color VARCHAR(30)
);

-- One-to-one: each character has one profile
CREATE TABLE more_info (
    more_info_id   SERIAL PRIMARY KEY,
    birthday       DATE,
    height_in_cm   INT,
    weight_in_kg   NUMERIC(4, 1),
    character_id   INT NOT NULL UNIQUE REFERENCES characters(character_id)
);

-- One-to-many: a character has many sounds
CREATE TABLE sounds (
    sound_id     SERIAL PRIMARY KEY,
    filename     VARCHAR(40) NOT NULL UNIQUE,
    character_id INT NOT NULL REFERENCES characters(character_id)
);

-- Many-to-many: characters <-> actions through a junction table
CREATE TABLE actions (
    action_id SERIAL PRIMARY KEY,
    action    VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE character_actions (
    character_id INT NOT NULL REFERENCES characters(character_id),
    action_id    INT NOT NULL REFERENCES actions(action_id),
    PRIMARY KEY (character_id, action_id)
);

-- 3. Data
INSERT INTO characters (name, homeland, favorite_color) VALUES
('Pip', 'Moss Hollow', 'Green'),
('Vera', 'Crystal Spire', 'Violet'),
('Grunk', 'Ember Caves', 'Orange'),
('Luma', 'Sky Harbor', 'Blue');

INSERT INTO more_info (birthday, height_in_cm, weight_in_kg, character_id) VALUES
('1990-04-12', 120, 30.5, 1),
('1992-09-30', 170, 58.0, 2),
('1988-01-05', 210, 140.2, 3),
(NULL, 150, NULL, 4);

INSERT INTO sounds (filename, character_id) VALUES
('pip-jump.wav', 1), ('pip-yay.wav', 1),
('vera-spell.wav', 2),
('grunk-roar.wav', 3), ('grunk-stomp.wav', 3);

INSERT INTO actions (action) VALUES ('run'), ('jump'), ('duck'), ('fly');

INSERT INTO character_actions (character_id, action_id) VALUES
(1, 1), (1, 2), (1, 3),
(2, 1), (2, 4),
(3, 1), (3, 3),
(4, 2), (4, 4);

-- 4. Queries
-- One-to-one join
SELECT
    chr.name,
    inf.birthday,
    inf.height_in_cm,
    COALESCE(inf.weight_in_kg::TEXT, 'unknown') AS weight_in_kg
FROM characters AS chr
JOIN more_info AS inf ON inf.character_id = chr.character_id
ORDER BY chr.character_id;

-- One-to-many: sound count per character (including those with none)
SELECT
    chr.name,
    COUNT(snd.sound_id) AS sound_count
FROM characters AS chr
LEFT JOIN sounds AS snd ON snd.character_id = chr.character_id
GROUP BY chr.name
ORDER BY sound_count DESC;

-- Many-to-many through the junction table
SELECT
    chr.name,
    STRING_AGG(act.action, ', ' ORDER BY act.action) AS actions
FROM characters AS chr
JOIN character_actions AS cha ON cha.character_id = chr.character_id
JOIN actions AS act           ON act.action_id = cha.action_id
GROUP BY chr.name
ORDER BY chr.name;
