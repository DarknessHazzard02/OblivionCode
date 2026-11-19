#!/bin/bash
# Made by: Hazzard
# FreeCodeCamp: Learn Bash and SQL by Building a Bike Rental Shop
# Interactive CLI that queries a PostgreSQL database to manage bike rentals

PSQL="psql --username=freecodecamp --dbname=bikes -t --no-align -c"

echo -e "\n~~~~~ Bike Rental Shop ~~~~~\n"

MAIN_MENU() {
  if [[ $1 ]]
  then
    echo -e "\n$1"
  fi

  echo "How may I help you?" 
  echo -e "\n1. Rent a bike\n2. Return a bike\n3. Exit"
  read MAIN_MENU_SELECTION

  case $MAIN_MENU_SELECTION in
    1) RENT_MENU ;;
    2) RETURN_MENU ;;
    3) EXIT ;;
    *) MAIN_MENU "Please enter a valid option." ;;
  esac
}

RENT_MENU() {
  AVAILABLE_BIKES=$($PSQL "SELECT bike_id, type, size FROM bikes WHERE available = true ORDER BY bike_id")

  if [[ -z $AVAILABLE_BIKES ]]
  then
    MAIN_MENU "Sorry, we don't have any bikes available right now."
  else
    echo -e "\nHere are the bikes we have available:\n"
    echo -e "ID\tType\t\tSize"
    echo "$AVAILABLE_BIKES" | while IFS="|" read BIKE_ID TYPE SIZE
    do
      echo -e "$BIKE_ID\t$TYPE\t\t${SIZE}\"" 
    done

    echo -e "\nWhich one would you like to rent? Enter the bike ID:"
    read BIKE_ID_TO_RENT

    # Validate the bike ID
    BIKE_AVAILABLE=$($PSQL "SELECT bike_id FROM bikes WHERE bike_id = $BIKE_ID_TO_RENT AND available = true")

    if [[ -z $BIKE_AVAILABLE ]]
    then
      RENT_MENU "That bike is not available. Please try again."
    else
      echo -e "\nWhat is your phone number?"
      read PHONE_NUMBER

      CUSTOMER_NAME=$($PSQL "SELECT name FROM customers WHERE phone = '$PHONE_NUMBER'")

      if [[ -z $CUSTOMER_NAME ]]
      then
        echo -e "\nWhat is your name?"
        read CUSTOMER_NAME
        INSERT_CUSTOMER=$($PSQL "INSERT INTO customers(name, phone) VALUES('$CUSTOMER_NAME', '$PHONE_NUMBER')")
      fi

      CUSTOMER_ID=$($PSQL "SELECT customer_id FROM customers WHERE phone = '$PHONE_NUMBER'")
      BIKE_TYPE=$($PSQL "SELECT type FROM bikes WHERE bike_id = $BIKE_ID_TO_RENT")
      BIKE_SIZE=$($PSQL "SELECT size FROM bikes WHERE bike_id = $BIKE_ID_TO_RENT")

      INSERT_RENTAL=$($PSQL "INSERT INTO rentals(customer_id, bike_id) VALUES($CUSTOMER_ID, $BIKE_ID_TO_RENT)")
      SET_AVAILABLE=$($PSQL "UPDATE bikes SET available = false WHERE bike_id = $BIKE_ID_TO_RENT")

      echo -e "\nI have put you down for the $BIKE_SIZE\" $BIKE_TYPE, $(echo $CUSTOMER_NAME | sed 's/^ *| *$//g')."
      MAIN_MENU
    fi
  fi
}

RETURN_MENU() {
  echo -e "\nWhat is your phone number?"
  read PHONE_NUMBER

  CUSTOMER_ID=$($PSQL "SELECT customer_id FROM customers WHERE phone = '$PHONE_NUMBER'")

  if [[ -z $CUSTOMER_ID ]]
  then
    MAIN_MENU "I could not find a record for that phone number."
  else
    CUSTOMER_RENTALS=$($PSQL "SELECT b.bike_id, b.type, b.size FROM bikes b INNER JOIN rentals r USING(bike_id) INNER JOIN customers c USING(customer_id) WHERE c.customer_id = $CUSTOMER_ID AND r.date_returned IS NULL ORDER BY b.bike_id")

    if [[ -z $CUSTOMER_RENTALS ]]
    then
      MAIN_MENU "You do not have any bikes rented."
    else
      CUSTOMER_NAME=$($PSQL "SELECT name FROM customers WHERE customer_id = $CUSTOMER_ID")
      echo -e "\nHere are your rentals, $(echo $CUSTOMER_NAME | sed 's/^ *| *$//g'):\n"
      echo -e "ID\tType\t\tSize"
      echo "$CUSTOMER_RENTALS" | while IFS="|" read BIKE_ID TYPE SIZE
      do
        echo -e "$BIKE_ID\t$TYPE\t\t${SIZE}\""
      done

      echo -e "\nWhich one would you like to return? Enter the bike ID:"
      read BIKE_ID_TO_RETURN

      RENTAL_ID=$($PSQL "SELECT rental_id FROM rentals WHERE customer_id = $CUSTOMER_ID AND bike_id = $BIKE_ID_TO_RETURN AND date_returned IS NULL")

      if [[ -z $RENTAL_ID ]]
      then
        RETURN_MENU "That is not a valid bike ID for your rentals. Please try again."
      else
        RETURN_BIKE=$($PSQL "UPDATE rentals SET date_returned = NOW() WHERE rental_id = $RENTAL_ID")
        SET_AVAILABLE=$($PSQL "UPDATE bikes SET available = true WHERE bike_id = $BIKE_ID_TO_RETURN")

        MAIN_MENU "Thank you for returning your bike!"
      fi
    fi
  fi
}

EXIT() {
  echo -e "\nThank you for stopping in.\n"
  exit 0
}

MAIN_MENU
