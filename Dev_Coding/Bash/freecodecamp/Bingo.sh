#!/bin/bash
# Made by: Hazzard
# FreeCodeCamp: Learn Bash Scripting by Building Five Programs (Bingo Generator)
# Teaches: Random number generation, Variables, Case statement

echo -e "\n~~ Bingo Number Generator ~~\n"

NUMBER=$(( RANDOM % 75 + 1 ))
TEXT="The next number is, "

if (( NUMBER <= 15 ))
then
    echo $TEXT B:$NUMBER
elif [[ $NUMBER -le 30 ]]
then
    echo $TEXT I:$NUMBER
elif (( NUMBER < 46 ))
then
    echo $TEXT N:$NUMBER
elif [[ $NUMBER -le 60 ]]
then
    echo $TEXT G:$NUMBER
else
    echo $TEXT O:$NUMBER
fi
