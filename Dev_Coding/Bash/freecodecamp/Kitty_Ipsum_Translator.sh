#!/bin/bash
# Made by: Hazzard
# FreeCodeCamp: Learn Advanced Bash by Building a Kitty Ipsum Translator
# Translates "kitty ipsum" text into "doggy ipsum" and reports word counts.
# Teaches: stdin/stdout/stderr redirection, pipes, sed with regex, grep -o,
#          wc, diff.
# Usage:  bash Kitty_Ipsum_Translator.sh            (uses built-in sample)
#         bash Kitty_Ipsum_Translator.sh < file.txt

# ==============================================================================
# Input: stdin if piped, otherwise a built-in sample
# ==============================================================================
[[ ! -t 0 ]] && INPUT="$(cat)"
if [[ -z $INPUT ]]
then
  INPUT="hiss at vacuum cleaner meow loudly just to annoy owners. catnip is
the best, meowzer! chase red dot then lose interest. cat cat cat sleep on
keyboard, purr purr. knock things off table because cat."
fi

# ==============================================================================
# Translator (same sed rules as the course's translate.sh)
# ==============================================================================
translate() {
  sed -E 's/catnip/dogchow/g; s/cat/dog/g; s/meowzer|meow/woof/g'
}

OUTPUT="$(echo "$INPUT" | translate)"

# ==============================================================================
# Report
# ==============================================================================
echo "~~ kitty_ipsum ~~"
echo "Number of lines:  $(echo "$INPUT" | wc -l)"
echo "Number of words:  $(echo "$INPUT" | wc -w)"
echo "Number of 'meow': $(echo "$INPUT" | grep -o 'meow[a-z]*' | wc -l)"
echo "Lines with 'cat': $(echo "$INPUT" | grep -n 'cat' | sed -E 's/([0-9]+).*/\1/' | tr '\n' ' ')"

echo -e "\n~~ doggy_ipsum ~~"
echo "$OUTPUT"

echo -e "\n~~ diff ~~"
diff <(echo "$INPUT") <(echo "$OUTPUT") --color=auto 2>/dev/null || true
