# Number Guessing Game

Guess a random number from 1 to 1000. Users and their best games are stored in PostgreSQL.

Source: freeCodeCamp, Relational Database certification.

## Files

| File | Language | Purpose |
|---|---|---|
| `Number_Guessing_Game.sql` | SQL (PostgreSQL) | Schema and seed data for the `number_guess` database |
| `Number_Guessing_Game.sh` | Bash | Script that talks to the database through `psql` |

## How to run

Needs PostgreSQL with a `freecodecamp` user, as in the freeCodeCamp environment.

```bash
psql --username=freecodecamp --dbname=postgres -f Number_Guessing_Game.sql   # the script creates number_guess and connects to it
bash Number_Guessing_Game.sh
```

---

*Made by: Hazzard*
