-- Made by: Hazzard
-- FreeCodeCamp Relational Database Certification
-- Project: Number Guessing Game (PostgreSQL)
-- Used by ../../Bash/freecodecamp/Number_Guessing_Game.sh

-- 1. Database
CREATE DATABASE number_guess;
\c number_guess

-- 2. Table Definitions
CREATE TABLE users (
    user_id      SERIAL PRIMARY KEY,
    username     VARCHAR(22) UNIQUE NOT NULL,
    games_played INT NOT NULL DEFAULT 0,
    best_game    INT
);

-- 3. Sample Data (invented players)
INSERT INTO users (username, games_played, best_game) VALUES
('player_one', 4, 7),
('night_owl', 2, 10);

-- 4. Queries
-- Leaderboard: fewest guesses first, players without games last
SELECT
    usr.username,
    usr.games_played,
    usr.best_game
FROM users AS usr
ORDER BY usr.best_game ASC NULLS LAST, usr.games_played DESC;
