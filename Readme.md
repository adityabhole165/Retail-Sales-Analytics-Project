# 🛒 Retail Sales Analytics Project
### Tech Stack: Python · SQL (SQLite) · Excel

---

## 📁 Project Folder Structure

```
retail_analytics_project/
│
├── run_project.py              ← ▶ MASTER RUNNER (start here)
├── requirements.txt            ← Python libraries to install
│
├── phase1_db_setup.py          ← Phase 1: Database creation
├── phase2_cleaning.py          ← Phase 2: Data cleaning
├── phase3_analysis.py          ← Phase 3: Charts & analysis
├── phase4_reporting.py         ← Phase 4: Excel dashboard
│
├── scripts/
│   └── generate_sample_data.py ← Creates sample CSV (auto-runs if needed)
│
├── data/                       ← CSV files go here
│   ├── retail_transactions.csv ← Raw data (Kaggle or auto-generated)
│   ├── retail_cleaned.csv      ← Cleaned output (auto-created)
│   ├── monthly_sales.csv       ← Analysis tables (auto-created)
│   ├── top_products.csv
│   ├── country_sales.csv
│   └── quarterly_summary.csv
│
├── database/
│   ├── schema.sql              ← SQL DDL (table definitions)
│   └── retail_analytics.db    ← SQLite database (auto-created)
│
└── reports/
    ├── Retail_Analytics_Report.xlsx  ← ✅ Final Excel Dashboard
    └── charts/
        ├── 01_monthly_trend.png
        ├── 02_top_products.png
        ├── 03_country_sales.png
        ├── 04_heatmap.png
        └── 05_mom_growth.png
```

---

## ⚙️ STEP-BY-STEP: How to Run

### STEP 1 — Install Python
- Go to https://www.python.org/downloads/
- Download Python 3.10 or higher
- During install, ✅ check **"Add Python to PATH"**
- Click Install

### STEP 2 — Download This Project
- Copy this entire `retail_analytics_project` folder to your computer
  (e.g., save it on your Desktop or in `C:\Projects\`)

### STEP 3 — Open Terminal / Command Prompt
**Windows:**
- Press `Windows + R`, type `cmd`, press Enter

**Mac:**
- Press `Cmd + Space`, type `Terminal`, press Enter

### STEP 4 — Navigate to the project folder
```bash
# Windows example (adjust path to where you saved it)
cd C:\Users\YourName\Desktop\retail_analytics_project

# Mac example
cd ~/Desktop/retail_analytics_project
```

### STEP 5 — Install Required Libraries
```bash
pip install -r requirements.txt
```
This installs: pandas, numpy, matplotlib, seaborn, openpyxl, Pillow

### STEP 6 — (Optional) Use Real Kaggle Data
If you want to use the real Kaggle dataset instead of sample data:
1. Go to https://www.kaggle.com/regivm/retailtransactiondata
2. Sign in to Kaggle and download the CSV
3. Rename the file to `retail_transactions.csv`
4. Place it inside the `data/` folder
5. Make sure columns match:
   `TransactionID, TransactionTime, ItemCode, ItemDescription,
    NumberOfItemsPurchased, CostPerItem, Country`

If you skip this step — **no problem!** The project will auto-generate
5,000 realistic sample transactions.

### STEP 7 — RUN THE PROJECT ▶
```bash
python run_project.py
```

That's it! All 4 phases run automatically. When complete, open:
```
reports/Retail_Analytics_Report.xlsx
```

---

## 📊 What Each Phase Does

### Phase 1 — Database Setup
- Reads the CSV file
- Creates a SQLite database (`retail_analytics.db`)
- Runs the SQL DDL in `schema.sql` to create 4 tables:
  - `dim_item` — product master
  - `dim_country` — country lookup
  - `dim_date` — date dimension (year, quarter, month, week, day)
  - `fact_sales` — all transactions with computed `total_sales_value`
- Loads all 5,000 rows into the database

### Phase 2 — Data Cleaning
- Connects to the database and runs a JOIN query across all tables
- Checks for **missing values** (nulls) in every column
- Detects **outliers** using the IQR (Interquartile Range) method
- Caps outliers instead of deleting them (safer for small datasets)
- Adds calculated fields: `total_sales_value`, `hour_of_day`, `week_number`
- Saves a clean CSV (`retail_cleaned.csv`) for use in analysis

### Phase 3 — Data Analysis
Generates 5 charts (saved as PNG):
| Chart | What it shows |
|-------|--------------|
| Monthly Trend | Revenue across each month (line chart) |
| Top Products | Best 10 products by total revenue (bar chart) |
| Country Sales | Revenue by country (bar chart) |
| Heatmap | Revenue by month × day-of-week (heatmap) |
| MoM Growth | Month-over-month % growth (bar chart) |

Also runs SQL queries for **quarterly revenue summaries**.

### Phase 4 — Excel Report
Creates a 6-sheet Excel workbook:
| Sheet | Contents |
|-------|----------|
| 📊 KPI Dashboard | 6 KPI cards + 4 embedded charts |
| 📅 Monthly Sales | Monthly revenue table with totals formula |
| 🛍️ Top Products | Product ranking with % of total |
| 🌍 Country Analysis | Country revenue breakdown |
| 📆 Quarterly Summary | Q1–Q4 revenue from SQL |
| 🗂️ Raw Data | Full 5,000-row cleaned dataset |

---

## 🛠️ Running Individual Phases

If you want to run only one phase:
```bash
python phase1_db_setup.py    # Database only
python phase2_cleaning.py    # Cleaning only (needs Phase 1 done first)
python phase3_analysis.py    # Charts only   (needs Phase 2 done first)
python phase4_reporting.py   # Excel only    (needs Phase 3 done first)
```

---

## ❓ Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `pip is not recognized` | Python not in PATH — reinstall Python and check "Add to PATH" |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| `FileNotFoundError: data/` | Make sure you are inside the project folder when running |
| `PermissionError on .xlsx` | Close the Excel file before running Phase 4 again |
| Excel file looks blank | Open it — Excel may ask to "Enable Editing" (click yes) |

---

## 📌 Key SQL Queries Used

```sql
-- Quarterly revenue
SELECT year, quarter, COUNT(*) AS transactions,
       SUM(total_sales_value) AS revenue
FROM   fact_sales f JOIN dim_date d ON f.date_id = d.date_id
GROUP  BY year, quarter;

-- Top products
SELECT item_description, SUM(total_sales_value) AS revenue
FROM   fact_sales f JOIN dim_item i ON f.item_code = i.item_code
GROUP  BY item_description ORDER BY revenue DESC;
```

---

*Generated by Python Analytics Pipeline — Retail Chain Project *