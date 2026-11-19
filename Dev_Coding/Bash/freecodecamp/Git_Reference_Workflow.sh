#!/bin/bash
# FreeCodeCamp: Learn Git by Building an SQL Reference Object
# Demonstrates iterative Git workflow: init, add, commit, branch, merge, rebase, stash, log

# NOTE: This is an educational simulation script showing the Git commands used in the freeCodeCamp course.
# Run each section in a real terminal with an actual Git repository for full effect.

REPO_DIR="sql_reference"

echo "=============================="
echo "  FreeCodeCamp Git Reference  "
echo "=============================="

echo -e "\n--- 1. Initialize Repository ---"
echo "git init $REPO_DIR"
echo "cd $REPO_DIR"
echo "git status"

echo -e "\n--- 2. First Commit ---"
echo 'touch sql_reference.json'
echo 'echo "{ \"create\": { \"row\": \"INSERT INTO table_name(columns) VALUES(values);\" } }" > sql_reference.json'
echo "git add sql_reference.json"
echo "git commit -m 'Initial commit'"

echo -e "\n--- 3. Working on a Feature Branch ---"
echo "git checkout -b feat/add-select-row"
echo "# Edit sql_reference.json to add SELECT row reference"
echo "git add sql_reference.json"
echo "git commit -m 'feat: add select row reference'"

echo -e "\n--- 4. Rebase onto main ---"
echo "git checkout main"
echo "git rebase feat/add-select-row"

echo -e "\n--- 5. Stash Uncommitted Changes ---"
echo "# While working on a half-done change:"
echo "git stash"
echo "# Switch context, then restore work:"
echo "git stash pop"

echo -e "\n--- 6. View History ---"
echo "git log --oneline --graph --all"

echo -e "\n--- 7. Reset & Clean ---"
echo "git reset HEAD~1       # Undo last commit, keep changes staged"
echo "git reset HEAD~1 --hard  # Undo last commit and discard changes"

echo -e "\n--- 8. Cherry Pick ---"
echo "git cherry-pick <commit-hash>  # Apply a specific commit to current branch"

echo -e "\n--- Reference: Key Git Commands ---"
printf "%-30s %s\n" "git init"             "Initialize a new repository"
printf "%-30s %s\n" "git status"           "Show working tree status"
printf "%-30s %s\n" "git add <file>"       "Stage a file for commit"
printf "%-30s %s\n" "git commit -m '...'"  "Commit staged changes"
printf "%-30s %s\n" "git branch <name>"    "Create a new branch"
printf "%-30s %s\n" "git checkout <name>"  "Switch to a branch"
printf "%-30s %s\n" "git merge <branch>"   "Merge a branch into current"
printf "%-30s %s\n" "git rebase <branch>"  "Reapply commits onto another branch"
printf "%-30s %s\n" "git stash"            "Temporarily save uncommitted changes"
printf "%-30s %s\n" "git log --oneline"    "Show condensed commit history"
printf "%-30s %s\n" "git reset HEAD~1"     "Undo last commit, keep staged"
printf "%-30s %s\n" "git cherry-pick <id>" "Apply a specific commit"
