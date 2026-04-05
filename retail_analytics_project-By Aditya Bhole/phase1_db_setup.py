"""
phase1_db_setup.py  (FIXED v3 – works with actual Kaggle CSV)
Actual CSV columns: customer_id, trans_date, tran_amount
"""

import os, sys, sqlite3, subprocess, random
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR   = os.path.join(BASE_DIR, "database")
CSV_PATH = os.path.join(DATA_DIR, "retail_transactions.csv")
DB_PATH  = os.path.join(DB_DIR,  "retail_analytics.db")
SCHEMA   = os.path.join(DB_DIR,  "schema.sql")

# ── Step 1: Load CSV (pandas 3.0 compatible – no 'errors' param) ──────────
if not os.path.exists(CSV_PATH):
    print(" CSV not found. Place retail_transactions.csv in the data/ folder.")
    sys.exit(1)

# Auto-detect separator
with open(CSV_PATH, "r", encoding="utf-8") as f:
    first_line = f.readline()
sep = ";" if first_line.count(";") > first_line.count(",") else ","

df_raw = pd.read_csv(CSV_PATH, sep=sep, encoding="utf-8", low_memory=False)
df_raw.columns = [c.strip().lower().replace(" ", "_") for c in df_raw.columns]

print(f"  Loaded CSV  →  {len(df_raw):,} rows")
print(f" Columns    →  {list(df_raw.columns)}")

# ── Step 2: Map actual Kaggle columns ──────────────────────────────────────
# Actual columns: customer_id, trans_date, tran_amount
col_map = {}
for col in df_raw.columns:
    c = col.lower().replace("_","").replace(" ","")
    if   c in ("customerid","customer_id","custid","cust"):          col_map["customer_id"]  = col
    elif c in ("transdate","trans_date","date","transactiondate",
               "transactiontime","transtime"):                        col_map["trans_date"]   = col
    elif c in ("tranamount","tran_amount","amount","totalsales",
               "salesvalue","revenue","price","cost","value"):        col_map["tran_amount"]  = col
    elif c in ("itemcode","item_code","productcode","sku"):           col_map["item_code"]    = col
    elif c in ("itemdescription","item_description","product",
               "productname","description"):                          col_map["item_desc"]    = col
    elif c in ("country","region","location"):                        col_map["country"]      = col
    elif c in ("quantity","qty","numberofitems","units",
               "numberofitemspurchased","numberofitemspurchased"):    col_map["quantity"]     = col

print(f"\n Detected mapping: {col_map}")

# ── Step 3: Build standardised dataframe ──────────────────────────────────
df = pd.DataFrame()

# TransactionID — use customer_id or auto-generate
if "customer_id" in col_map:
    df["TransactionID"] = df_raw[col_map["customer_id"]].astype(str).str.strip()
else:
    df["TransactionID"] = [f"TXN{i:06d}" for i in range(1, len(df_raw)+1)]

# TransactionTime
if "trans_date" in col_map:
    df["TransactionTime"] = pd.to_datetime(df_raw[col_map["trans_date"]], 
                                           errors="coerce")
else:
    df["TransactionTime"] = pd.to_datetime("2023-01-01")

# CostPerItem / TranAmount
if "tran_amount" in col_map:
    df["CostPerItem"] = pd.to_numeric(df_raw[col_map["tran_amount"]], errors="coerce")
elif "quantity" in col_map and "item_code" in col_map:
    df["CostPerItem"] = pd.to_numeric(df_raw.get("cost", 10.0), errors="coerce")
else:
    df["CostPerItem"] = 10.0

# NumberOfItems
if "quantity" in col_map:
    df["NumberOfItems"] = pd.to_numeric(df_raw[col_map["quantity"]], errors="coerce").fillna(1).astype(int)
else:
    df["NumberOfItems"] = 1   # default — 1 item per transaction

# ItemCode & ItemDescription — generate if not in CSV
ITEMS = [
    ("ITM001","Wireless Mouse"),("ITM002","USB Keyboard"),("ITM003","HDMI Cable"),
    ("ITM004","Laptop Stand"),("ITM005","Webcam HD"),("ITM006","Headphones"),
    ("ITM007","Phone Charger"),("ITM008","Screen Cleaner"),("ITM009","Desk Lamp"),
    ("ITM010","Power Strip"),("ITM011","Notebook"),("ITM012","Pen Set"),
    ("ITM013","Stapler"),("ITM014","Sticky Notes"),("ITM015","Folder Set"),
]
if "item_code" in col_map:
    df["ItemCode"]        = df_raw[col_map["item_code"]].astype(str)
    df["ItemDescription"] = df_raw[col_map.get("item_desc","item_code")].astype(str) \
                            if "item_desc" in col_map else df["ItemCode"]
else:
    choices = random.choices(ITEMS, k=len(df_raw))
    df["ItemCode"]        = [c[0] for c in choices]
    df["ItemDescription"] = [c[1] for c in choices]

# Country — generate if not in CSV
COUNTRIES = ["United Kingdom","Germany","France","Australia",
             "United States","Netherlands","Spain","Belgium"]
if "country" in col_map:
    df["Country"] = df_raw[col_map["country"]].astype(str).str.strip()
else:
    df["Country"] = random.choices(
        COUNTRIES, weights=[35,15,12,8,10,8,7,5], k=len(df_raw))

# ── Step 4: Clean ─────────────────────────────────────────────────────────
df.dropna(subset=["TransactionTime"], inplace=True)
df["CostPerItem"]   = df["CostPerItem"].fillna(df["CostPerItem"].median())
df["NumberOfItems"] = df["NumberOfItems"].clip(lower=1)
df["Country"]       = df["Country"].replace({"nan":"Unknown","":"Unknown"}).fillna("Unknown")
df["DateID"]        = df["TransactionTime"].dt.date.astype(str)

# Make TransactionID unique (customer can have multiple rows)
df = df.reset_index(drop=True)
df["TransactionID"] = df["TransactionID"].astype(str) + "_" + df.index.astype(str)

print(f"  Clean rows: {len(df):,}")
print(f"   Date range : {df['TransactionTime'].min().date()} → {df['TransactionTime'].max().date()}")
print(f"   Revenue    : £{(df['CostPerItem']*df['NumberOfItems']).sum():,.2f}")

# ── Step 5: Create database ───────────────────────────────────────────────
os.makedirs(DB_DIR, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()
with open(SCHEMA, "r") as f:
    cur.executescript(f.read())
conn.commit()
print(f"\n   Database  →  {DB_PATH}")

# ── Step 6: dim_item ──────────────────────────────────────────────────────
items = df[["ItemCode","ItemDescription"]].drop_duplicates("ItemCode").copy()
items.columns = ["item_code","item_description"]
items.to_sql("dim_item", conn, if_exists="append", index=False)
print(f"   dim_item     → {len(items)} rows")

# ── Step 7: dim_country ───────────────────────────────────────────────────
for c in df["Country"].unique():
    cur.execute("INSERT OR IGNORE INTO dim_country(country_name) VALUES (?)", (c,))
conn.commit()
country_map = dict(pd.read_sql("SELECT country_name, country_id FROM dim_country", conn).values)
print(f"   dim_country  → {len(country_map)} rows")

# ── Step 8: dim_date ──────────────────────────────────────────────────────
MONTH_NAMES = {1:"January",2:"February",3:"March",4:"April",5:"May",
               6:"June",7:"July",8:"August",9:"September",
               10:"October",11:"November",12:"December"}
dates_df  = df[["DateID","TransactionTime"]].drop_duplicates("DateID")
date_rows = []
for _, row in dates_df.iterrows():
    dt = row["TransactionTime"]
    date_rows.append({
        "date_id":    row["DateID"],
        "year":       dt.year,
        "quarter":    (dt.month-1)//3+1,
        "month":      dt.month,
        "month_name": MONTH_NAMES[dt.month],
        "week":       int(dt.isocalendar()[1]),
        "day_of_week":dt.strftime("%A"),
    })
pd.DataFrame(date_rows).to_sql("dim_date", conn, if_exists="append", index=False)
print(f"   dim_date     → {len(date_rows)} rows")

# ── Step 9: fact_sales ────────────────────────────────────────────────────
df["country_id"] = df["Country"].map(country_map)
fact = df[["TransactionID","TransactionTime","DateID",
           "ItemCode","country_id","NumberOfItems","CostPerItem"]].copy()
fact.columns = ["transaction_id","transaction_time","date_id",
                "item_code","country_id","number_of_items","cost_per_item"]
fact["transaction_time"] = fact["transaction_time"].astype(str)
fact.to_sql("fact_sales", conn, if_exists="append", index=False)
print(f"   fact_sales   → {len(fact):,} rows")

conn.close()
print("\n Phase 1 complete – database ready.")