#!/bin/bash
# Made by: Hazzard
# FreeCodeCamp: Learn Bash Scripting by Building Five Programs (Questionnaire)
# Teaches: User input with read, string variables, formatting

echo -e "\n~~ Questionnaire ~~\n"

QUESTION1="What's your name?"
QUESTION2="Where are you from?"
QUESTION3="What's your favorite coding language?"

# Provide defaults if running non-interactively
if [ -t 0 ]; then
    echo $QUESTION1
    read NAME
    echo $QUESTION2
    read LOCATION
    echo $QUESTION3
    read FAVORITE_LANGUAGE
else
    NAME="Hazzard"
    LOCATION="Earth"
    FAVORITE_LANGUAGE="Python"
fi

echo -e "\nHello $NAME from $LOCATION. I learned that your favorite programming language is $FAVORITE_LANGUAGE!"
