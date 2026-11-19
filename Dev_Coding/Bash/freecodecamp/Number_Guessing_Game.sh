#!/bin/bash
# Made by: Hazzard
# FreeCodeCamp Relational Database Certification - Number Guessing Game
# Bash + PostgreSQL. Schema in ../../SQL/freecodecamp/Number_Guessing_Game.sql
# Teaches: psql from Bash, input validation, persisting game stats.
# Set NO_DB=1 to play without a database.

PSQL="psql --username=freecodecamp --dbname=number_guess -t --no-align -c"

db() {
  [[ $NO_DB == 1 ]] && return 0
  $PSQL "$1"
}

SECRET_NUMBER=$(( RANDOM % 1000 + 1 ))

echo "Enter your username:"
read USERNAME

if [[ ${#USERNAME} -gt 22 || -z $USERNAME ]]
then
  echo "Username must be 1-22 characters."
  exit 1
fi

SAFE_USERNAME=${USERNAME//\'/\'\'}
USER_INFO=$(db "SELECT games_played, best_game FROM users WHERE username='$SAFE_USERNAME'")

if [[ -z $USER_INFO ]]
then
  echo "Welcome, $USERNAME! It looks like this is your first time here."
  db "INSERT INTO users(username) VALUES('$SAFE_USERNAME')" > /dev/null
else
  IFS="|" read GAMES_PLAYED BEST_GAME <<< "$USER_INFO"
  echo "Welcome back, $USERNAME! You have played $GAMES_PLAYED games, and your best game took $BEST_GAME guesses."
fi

echo "Guess the secret number between 1 and 1000:"
TRIES=0
while true
do
  read GUESS || { echo "No more input, exiting."; exit 1; }
  if [[ ! $GUESS =~ ^[0-9]+$ ]]
  then
    echo "That is not an integer, guess again:"
    continue
  fi
  (( TRIES++ ))
  if (( GUESS > SECRET_NUMBER ))
  then
    echo "It's lower than that, guess again:"
  elif (( GUESS < SECRET_NUMBER ))
  then
    echo "It's higher than that, guess again:"
  else
    break
  fi
done

db "UPDATE users
    SET games_played = games_played + 1,
        best_game = LEAST(COALESCE(best_game, $TRIES), $TRIES)
    WHERE username = '$SAFE_USERNAME'" > /dev/null

echo "You guessed it in $TRIES tries. The secret number was $SECRET_NUMBER. Nice job!"
