#!/bin/bash
# FreeCodeCamp: Learn Bash Scripting by Building a Countdown Timer
# Teaches: Command line arguments, While loops, Until loops, Conditionals

echo -e "\n~~ Countdown Timer ~~\n"

if [[ $1 -gt 0 ]]
then
    I=$1
    while [[ $I -ge 0 ]]
    do
        echo "$I"
        (( I-- ))
        sleep 0.1 # Using 0.1 for swift testing instead of 1s
    done
else
    echo "Include a positive integer as the first argument."
fi
