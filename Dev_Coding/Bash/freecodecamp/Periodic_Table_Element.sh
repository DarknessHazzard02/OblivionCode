#!/bin/bash
# Made by: Hazzard
# FreeCodeCamp Relational Database Certification - Periodic Table Database
# Looks up an element by atomic number, symbol or name.
# Schema in ../../SQL/freecodecamp/Periodic_Table_Database.sql
# Usage: ./Periodic_Table_Element.sh 1 | H | Hydrogen

PSQL="psql --username=freecodecamp --dbname=periodic_table -t --no-align -c"

if [[ -z $1 ]]
then
  echo "Please provide an element as an argument."
  exit 0
fi

ARG=${1//\'/\'\'}

if [[ $ARG =~ ^[0-9]+$ ]]
then
  WHERE="e.atomic_number = $ARG"
else
  WHERE="e.symbol = '$ARG' OR e.name = '$ARG'"
fi

RESULT=$($PSQL "SELECT e.atomic_number, e.name, e.symbol, t.type,
                       p.atomic_mass, p.melting_point_celsius, p.boiling_point_celsius
                FROM elements AS e
                JOIN properties AS p USING (atomic_number)
                JOIN types AS t USING (type_id)
                WHERE $WHERE")

if [[ -z $RESULT ]]
then
  echo "I could not find that element in the database."
  exit 0
fi

IFS="|" read NUMBER NAME SYMBOL TYPE MASS MELT BOIL <<< "$RESULT"
echo "The element with atomic number $NUMBER is $NAME ($SYMBOL). It's a $TYPE, with a mass of $MASS amu. $NAME has a melting point of $MELT celsius and a boiling point of $BOIL celsius."
