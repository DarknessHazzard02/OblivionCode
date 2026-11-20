-- Made by: Hazzard
-- S&OP star schema: three dimensions (date, production line, item) and two facts
-- (production by line and day, inventory by item and day). Portable SQL: runs on SQLite
-- for the demo and maps directly to SQL Server / Fabric warehouse types.

CREATE TABLE dim_date (
    date_key        INTEGER PRIMARY KEY,          -- YYYYMMDD
    calendar_date   TEXT    NOT NULL UNIQUE,      -- ISO date
    iso_week        TEXT    NOT NULL,             -- e.g. 2026-W02
    month_name      TEXT    NOT NULL,
    is_workday      INTEGER NOT NULL CHECK (is_workday IN (0, 1))
);

CREATE TABLE dim_line (
    line_key        INTEGER PRIMARY KEY,
    line_code       TEXT    NOT NULL UNIQUE,
    area            TEXT    NOT NULL
);

CREATE TABLE dim_item (
    item_key        INTEGER PRIMARY KEY,
    item_code       TEXT    NOT NULL UNIQUE,
    family          TEXT    NOT NULL,
    safety_stock    REAL    NOT NULL CHECK (safety_stock >= 0)
);

-- One row per line and day. Times in minutes, ideal cycle in seconds per unit.
CREATE TABLE fact_production (
    date_key            INTEGER NOT NULL REFERENCES dim_date (date_key),
    line_key            INTEGER NOT NULL REFERENCES dim_line (line_key),
    item_key            INTEGER NOT NULL REFERENCES dim_item (item_key),
    planned_qty         REAL    NOT NULL CHECK (planned_qty >= 0),
    actual_qty          REAL    NOT NULL CHECK (actual_qty >= 0),
    good_qty            REAL    NOT NULL CHECK (good_qty >= 0),
    planned_time_min    REAL    NOT NULL CHECK (planned_time_min > 0),
    run_time_min        REAL    NOT NULL CHECK (run_time_min >= 0),
    ideal_cycle_sec     REAL    NOT NULL CHECK (ideal_cycle_sec > 0),
    PRIMARY KEY (date_key, line_key, item_key),
    CHECK (good_qty <= actual_qty),
    CHECK (run_time_min <= planned_time_min)
);

-- One row per item and day.
CREATE TABLE fact_inventory (
    date_key            INTEGER NOT NULL REFERENCES dim_date (date_key),
    item_key            INTEGER NOT NULL REFERENCES dim_item (item_key),
    on_hand_qty         REAL    NOT NULL CHECK (on_hand_qty >= 0),
    forecast_daily_qty  REAL    NOT NULL CHECK (forecast_daily_qty >= 0),
    PRIMARY KEY (date_key, item_key)
);
