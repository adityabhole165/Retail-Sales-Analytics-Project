"""
phase3_analysis.py
------------------
PHASE 3 – Data Analysis & Exploration

Produces:
  • Monthly sales trend (line chart)
  • Top 10 products by revenue (bar chart)
  • Sales by country (horizontal bar)
  • Sales heatmap by month × weekday
  • Quarterly revenue summary (SQL)
  • Cohort-style repeat-purchase analysis
All charts saved as PNG inside reports/charts/
"""

import os, sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "database", "retail_analytics.db")
CHARTS_DIR = os.path.join(BASE_DIR, "reports", "charts")
DATA_DIR   = os.path.join(BASE_DIR, "data")
os.makedirs(CHARTS_DIR, exist_ok=True)

PALETTE = ["#1a5f7a", "#2d9cdb", "#56ccf2", "#f2994a", "#eb5757",
           "#27ae60", "#9b51e0", "#f2c94c", "#219653", "#bb6bd9"]
sns.set_theme(style="whitegrid", palette=PALETTE)

# ── Load cleaned data ──────────────────────────────────────────────────────
csv_path = os.path.join(DATA_DIR, "retail_cleaned.csv")
df = pd.read_csv(csv_path, parse_dates=["transaction_time"])

print("=" * 60)
print("PHASE 3 – DATA ANALYSIS")
print("=" * 60)

# ─────────────────────────────────────────────────────────────────────────
# 3.1  SQL – Quarterly Revenue Summary
# ─────────────────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
quarterly = pd.read_sql("""
    SELECT  d.year,
            d.quarter,
            COUNT(*)                   AS transactions,
            SUM(f.total_sales_value)   AS revenue,
            AVG(f.total_sales_value)   AS avg_order_value
    FROM    fact_sales f
    JOIN    dim_date   d ON f.date_id = d.date_id
    GROUP   BY d.year, d.quarter
    ORDER   BY d.year, d.quarter
""", conn)
conn.close()

print("\n Quarterly Revenue (SQL):")
print(quarterly.to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────
# 3.2  Monthly Sales Trend
# ─────────────────────────────────────────────────────────────────────────
monthly = (df.groupby(["year", "month", "month_name"])["total_sales_value"]
             .sum().reset_index())
monthly["period"] = monthly["month_name"].str[:3] + " " + monthly["year"].astype(str)
monthly.sort_values(["year", "month"], inplace=True)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly["period"], monthly["total_sales_value"],
        marker="o", color=PALETTE[0], linewidth=2.5, markersize=6)
ax.fill_between(monthly["period"], monthly["total_sales_value"],
                alpha=0.15, color=PALETTE[0])
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.set_title("Monthly Sales Revenue Trend", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Month"); ax.set_ylabel("Revenue")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
chart1 = os.path.join(CHARTS_DIR, "01_monthly_trend.png")
fig.savefig(chart1, dpi=150); plt.close()
print(f"\n Chart saved → {chart1}")

# ─────────────────────────────────────────────────────────────────────────
# 3.3  Top 10 Products by Revenue
# ─────────────────────────────────────────────────────────────────────────
top_products = (df.groupby("item_description")["total_sales_value"]
                  .sum().nlargest(10).reset_index())
top_products.columns = ["Product", "Revenue"]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(top_products["Product"][::-1], top_products["Revenue"][::-1],
               color=PALETTE[:10])
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.set_title("Top 10 Products by Revenue", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Total Revenue")
for bar in bars:
    ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
            f"{bar.get_width():,.0f}", va="center", fontsize=8)
plt.tight_layout()
chart2 = os.path.join(CHARTS_DIR, "02_top_products.png")
fig.savefig(chart2, dpi=150); plt.close()
print(f"  Chart saved → {chart2}")

# ─────────────────────────────────────────────────────────────────────────
# 3.4  Sales by Country
# ─────────────────────────────────────────────────────────────────────────
by_country = (df.groupby("country")["total_sales_value"]
                .sum().sort_values(ascending=False).reset_index())
by_country.columns = ["Country", "Revenue"]

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(by_country["Country"], by_country["Revenue"],
       color=PALETTE[:len(by_country)])
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.set_title("Total Revenue by Country", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Country"); ax.set_ylabel("Revenue")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
chart3 = os.path.join(CHARTS_DIR, "03_country_sales.png")
fig.savefig(chart3, dpi=150); plt.close()
print(f"Chart saved → {chart3}")

# ─────────────────────────────────────────────────────────────────────────
# 3.5  Heatmap – Revenue by Month × Day-of-Week
# ─────────────────────────────────────────────────────────────────────────
DOW_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
heat_df = (df.groupby(["month_name", "day_of_week"])["total_sales_value"]
             .sum().reset_index())
MONTH_ORDER = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
heat_pivot = heat_df.pivot(index="day_of_week", columns="month_name",
                            values="total_sales_value")
heat_pivot = heat_pivot.reindex(index=DOW_ORDER,
                                 columns=[m for m in MONTH_ORDER if m in heat_pivot.columns])

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(heat_pivot, ax=ax, cmap="Blues",
            fmt=".0f", linewidths=0.5,
            cbar_kws={"label": "Revenue "})
ax.set_title("Revenue Heatmap – Month × Day of Week",
             fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Month"); ax.set_ylabel("")
plt.tight_layout()
chart4 = os.path.join(CHARTS_DIR, "04_heatmap.png")
fig.savefig(chart4, dpi=150); plt.close()
print(f"Chart saved → {chart4}")

# ─────────────────────────────────────────────────────────────────────────
# 3.6  Advanced – Monthly Revenue Growth (%)
# ─────────────────────────────────────────────────────────────────────────
monthly["growth_pct"] = monthly["total_sales_value"].pct_change() * 100

fig, ax = plt.subplots(figsize=(12, 4))
colors = [PALETTE[3] if g >= 0 else PALETTE[4] for g in monthly["growth_pct"].fillna(0)]
ax.bar(monthly["period"], monthly["growth_pct"].fillna(0), color=colors)
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_title("Month-over-Month Revenue Growth (%)", fontsize=14,
             fontweight="bold", pad=12)
ax.set_xlabel("Month"); ax.set_ylabel("Growth %")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
chart5 = os.path.join(CHARTS_DIR, "05_mom_growth.png")
fig.savefig(chart5, dpi=150); plt.close()
print(f" Chart saved → {chart5}")

# ─────────────────────────────────────────────────────────────────────────
# 3.7  Summary stats saved for Phase 4
# ─────────────────────────────────────────────────────────────────────────
summary = {
    "total_revenue":    df["total_sales_value"].sum(),
    "total_txns":       len(df),
    "avg_order_value":  df["total_sales_value"].mean(),
    "top_product":      top_products.iloc[0]["Product"],
    "top_country":      by_country.iloc[0]["Country"],
}
print("\n Key Metrics:")
for k, v in summary.items():
    print(f"    {k:<22} {v}")

# save analysis tables
monthly.to_csv(os.path.join(DATA_DIR, "monthly_sales.csv"), index=False)
top_products.to_csv(os.path.join(DATA_DIR, "top_products.csv"), index=False)
by_country.to_csv(os.path.join(DATA_DIR, "country_sales.csv"), index=False)
quarterly.to_csv(os.path.join(DATA_DIR, "quarterly_summary.csv"), index=False)

print("\n Phase 3 complete – all charts and analysis tables saved.")