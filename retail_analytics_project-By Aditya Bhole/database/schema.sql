-- =============================================================
--  schema.sql  –  Retail Analytics Database Schema
--  Database : SQLite  (file: retail_analytics.db)
-- =============================================================

-- Drop tables if they already exist (safe re-run)
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_item;
DROP TABLE IF EXISTS dim_country;
DROP TABLE IF EXISTS dim_date;

-- -------------------------------------------------------------
-- Dimension: Item
-- -------------------------------------------------------------
CREATE TABLE dim_item (
    item_code        TEXT PRIMARY KEY,
    item_description TEXT NOT NULL
);

-- -------------------------------------------------------------
-- Dimension: Country
-- -------------------------------------------------------------
CREATE TABLE dim_country (
    country_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    country_name TEXT UNIQUE NOT NULL
);

-- -------------------------------------------------------------
-- Dimension: Date  (pre-populated by Python from transaction dates)
-- -------------------------------------------------------------
CREATE TABLE dim_date (
    date_id    TEXT PRIMARY KEY,   -- 'YYYY-MM-DD'
    year       INTEGER NOT NULL,
    quarter    INTEGER NOT NULL,
    month      INTEGER NOT NULL,
    month_name TEXT    NOT NULL,
    week       INTEGER NOT NULL,
    day_of_week TEXT   NOT NULL
);

-- -------------------------------------------------------------
-- Fact: Sales Transactions
-- -------------------------------------------------------------
CREATE TABLE fact_sales (
    transaction_id          TEXT    PRIMARY KEY,
    transaction_time        TEXT    NOT NULL,
    date_id                 TEXT    NOT NULL REFERENCES dim_date(date_id),
    item_code               TEXT    NOT NULL REFERENCES dim_item(item_code),
    country_id              INTEGER NOT NULL REFERENCES dim_country(country_id),
    number_of_items         INTEGER NOT NULL CHECK(number_of_items > 0),
    cost_per_item           REAL    NOT NULL CHECK(cost_per_item >= 0),
    total_sales_value       REAL    GENERATED ALWAYS AS
                                (number_of_items * cost_per_item) STORED
);

-- -------------------------------------------------------------
-- Useful indexes for query performance
-- -------------------------------------------------------------
CREATE INDEX idx_sales_date    ON fact_sales(date_id);
CREATE INDEX idx_sales_item    ON fact_sales(item_code);
CREATE INDEX idx_sales_country ON fact_sales(country_id);