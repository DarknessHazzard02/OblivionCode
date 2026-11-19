-- FreeCodeCamp Relational Database Certification
-- Project: World Cup Database
-- Schema, Sample Data, and Analytical Queries

-- 1. Table Definitions
CREATE TABLE teams (
    team_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE games (
    game_id SERIAL PRIMARY KEY,
    year INT NOT NULL,
    round VARCHAR(30) NOT NULL,
    winner_id INT NOT NULL REFERENCES teams(team_id),
    opponent_id INT NOT NULL REFERENCES teams(team_id),
    winner_goals INT NOT NULL,
    opponent_goals INT NOT NULL
);

-- 2. Insert Teams
INSERT INTO teams (name) VALUES
('France'), ('Croatia'), ('Belgium'), ('England'),
('Russia'), ('Sweden'), ('Brazil'), ('Uruguay'),
('Argentina'), ('Portugal'), ('Spain'), ('Colombia');

-- 3. Insert Games (Sample 2018 Tournament Knockout Matches)
INSERT INTO games (year, round, winner_id, opponent_id, winner_goals, opponent_goals) VALUES
(2018, 'Final', 1, 2, 4, 2),              -- France vs Croatia
(2018, 'Third Place', 3, 4, 2, 0),        -- Belgium vs England
(2018, 'Semi-Final', 1, 3, 1, 0),         -- France vs Belgium
(2018, 'Semi-Final', 2, 4, 2, 1),         -- Croatia vs England
(2018, 'Quarter-Final', 1, 8, 2, 0),      -- France vs Uruguay
(2018, 'Quarter-Final', 3, 7, 2, 1),      -- Belgium vs Brazil
(2018, 'Quarter-Final', 4, 6, 2, 0),      -- England vs Sweden
(2018, 'Quarter-Final', 2, 5, 3, 2);      -- Croatia vs Russia

-- 4. FCC Challenge Queries:

-- Total number of goals in all games from winning teams:
SELECT SUM(winner_goals) AS total_winner_goals FROM games;

-- Total number of goals in all games from both teams combined:
SELECT SUM(winner_goals + opponent_goals) AS total_goals FROM games;

-- Average number of goals in all games from winning teams:
SELECT AVG(winner_goals) AS avg_winner_goals FROM games;

-- Average number of goals in all games from winning teams rounded to two decimal places:
SELECT ROUND(AVG(winner_goals), 2) AS rounded_avg_winner_goals FROM games;

-- Average number of goals in all games from both teams:
SELECT ROUND(AVG(winner_goals + opponent_goals), 2) AS avg_total_goals FROM games;

-- Most goals scored in a single game by one team:
SELECT MAX(winner_goals) AS max_single_game_goals FROM games;

-- List of unique winning team names in alphabetical order:
SELECT DISTINCT(t.name) 
FROM games g
JOIN teams t ON g.winner_id = t.team_id
ORDER BY t.name;

-- Year and team name of all the champions:
SELECT g.year, t.name 
FROM games g
JOIN teams t ON g.winner_id = t.team_id
WHERE g.round = 'Final'
ORDER BY g.year;
