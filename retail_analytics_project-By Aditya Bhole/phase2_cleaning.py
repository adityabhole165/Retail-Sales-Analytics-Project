"""
phase2_cleaning.py
------------------
PHASE 2 – Data Cleaning & Preparation

Demonstrates:
  • Missing-value detection & handling
  • Outlier detection (IQR method)
  • Duplicate removal
  • Calculated fields (TotalSalesValue, Month, Year, Quarter)
  • Saves cleaned data to CSV and updates the SQLite fact table
"""

import os, sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database", "retail_analytics.db")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ── Load from database ─────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    f.transaction_id,
    f.transaction_time,
    d.year,
    d.quarter,
    d.month,
    d.month_name,
    d.day_of_week,
    f.item_code,
    i.item_description,
    f.number_of_items,
    f.cost_per_item,
    f.total_sales_value,
    c.country_name AS country
FROM  fact_sales   f
JOIN  dim_date     d ON f.date_id    = d.date_id
JOIN  dim_item     i ON f.item_code  = i.item_code
JOIN  dim_country  c ON f.country_id = c.country_id
"""

df = pd.read_sql(query, conn)
conn.close()

print("=" * 60)
print("PHASE 2 – DATA CLEANING & PREPARATION")
print("=" * 60)
print(f"\n  Raw rows loaded from DB : {len(df):,}")

# ── 2.1 Duplicate Detection ────────────────────────────────────────────────
dupes = df.duplicated(subset="transaction_id").sum()
df.drop_duplicates(subset="transaction_id", inplace=True)
print(f"  Duplicates removed      : {dupes}")

# ── 2.2 Missing Values Report ─────────────────────────────────────────────
print("\n Missing values per column:")
missing = df.isnull().sum()
missing = missing[missing > 0]
if missing.empty:
    print("      No missing values found.")
else:
    for col, cnt in missing.items():
        pct = cnt / len(df) * 100
        print(f"    {col:<28} {cnt:>5}  ({pct:.1f}%)")

# ── 2.3 Outlier Detection (IQR) ───────────────────────────────────────────
def flag_outliers(series, label):
    Q1, Q3 = series.quantile(0.25), series.quantile(0.75)
    IQR     = Q3 - Q1
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    mask = (series < lower) | (series > upper)
    print(f"    {label:<28} outliers={mask.sum():>4}  "
          f"(lower={lower:.2f}, upper={upper:.2f})")
    return mask

print("\n  Outlier detection (IQR method):")
out_qty   = flag_outliers(df["number_of_items"], "number_of_items")
out_cost  = flag_outliers(df["cost_per_item"],   "cost_per_item")

# Cap outliers instead of dropping (preserves data volume)
for col, mask in [("number_of_items", out_qty), ("cost_per_item", out_cost)]:
    Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    IQR = Q3 - Q1
    df.loc[mask & (df[col] < Q1 - 1.5*IQR), col] = Q1 - 1.5*IQR
    df.loc[mask & (df[col] > Q3 + 1.5*IQR), col] = Q3 + 1.5*IQR
print("      Outliers capped at IQR boundaries.")

# ── 2.4 Calculated Fields ──────────────────────────────────────────────────
df["total_sales_value"] = (df["number_of_items"] * df["cost_per_item"]).round(2)
df["transaction_time"]  = pd.to_datetime(df["transaction_time"])
df["hour_of_day"]       = df["transaction_time"].dt.hour
df["week_number"]       = df["transaction_time"].dt.isocalendar().week.astype(int)

print("\n  Calculated fields added:")
print("    • total_sales_value  = number_of_items × cost_per_item")
print("    • hour_of_day        = hour extracted from TransactionTime")
print("    • week_number        = ISO week number")

# ── 2.5 Summary statistics ────────────────────────────────────────────────
print("\n Cleaned dataset summary:")
print(df[["number_of_items", "cost_per_item", "total_sales_value"]].describe().round(2))

# ── 2.6 Save cleaned CSV ──────────────────────────────────────────────────
out_csv = os.path.join(DATA_DIR, "retail_cleaned.csv")
df.to_csv(out_csv, index=False)
print(f"\n  Cleaned data saved → {out_csv}  ({len(df):,} rows)")
print("\n  Phase 2 complete.")