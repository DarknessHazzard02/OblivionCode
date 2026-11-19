#!/bin/bash
# Made by: Hazzard
# FreeCodeCamp: Learn Bash Scripting by Building Five Programs - Five
# Runs the other four programs in sequence (questionnaire, countdown,
# bingo, fortune). Teaches: calling scripts, script directory resolution.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for PROGRAM in Questionnaire.sh "Countdown.sh 3" Bingo.sh Fortune.sh
do
  echo -e "\n==== Running $PROGRAM ===="
  # shellcheck disable=SC2086
  bash "$SCRIPT_DIR"/$PROGRAM || echo "!! $PROGRAM exited with an error"
done
