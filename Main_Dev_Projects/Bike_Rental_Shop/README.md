# Bike Rental Shop

Menu-driven CLI to rent and return bikes, backed by PostgreSQL.

Source: freeCodeCamp, Relational Database certification.

## Files

| File | Language | Purpose |
|---|---|---|
| `Bike_Rental_Database.sql` | SQL (PostgreSQL) | Schema and seed data for the `bikes` database |
| `Bike_Rental_Shop.sh` | Bash | Script that talks to the database through `psql` |

## How to run

Needs PostgreSQL with a `freecodecamp` user, as in the freeCodeCamp environment.

```bash
createdb --username=freecodecamp bikes
psql --username=freecodecamp --dbname=bikes -f Bike_Rental_Database.sql
bash Bike_Rental_Shop.sh
```

---

*Made by: Hazzard*
