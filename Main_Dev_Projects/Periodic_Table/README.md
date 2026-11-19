# Periodic Table

Look up an element by atomic number, symbol or name. Usage: `bash Periodic_Table_Element.sh H`.

Source: freeCodeCamp, Relational Database certification.

## Files

| File | Language | Purpose |
|---|---|---|
| `Periodic_Table_Database.sql` | SQL (PostgreSQL) | Schema and seed data for the `periodic_table` database |
| `Periodic_Table_Element.sh` | Bash | Script that talks to the database through `psql` |

## How to run

Needs PostgreSQL with a `freecodecamp` user, as in the freeCodeCamp environment.

```bash
psql --username=freecodecamp --dbname=postgres -f Periodic_Table_Database.sql   # the script creates periodic_table and connects to it
bash Periodic_Table_Element.sh H
```

---

*Made by: Hazzard*
