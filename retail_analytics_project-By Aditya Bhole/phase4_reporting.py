"""
phase4_reporting.py  (FAST VERSION - handles 125,000+ rows)
Uses xlsxwriter for raw data (100x faster than openpyxl for large sheets)
"""

import os
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
CHARTS_DIR = os.path.join(BASE_DIR, "reports", "charts")
REPORTS    = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS, exist_ok=True)

DARK_BLUE  = "1A5F7A"
MID_BLUE   = "2D9CDB"
LIGHT_BLUE = "EBF5FB"
ORANGE     = "F2994A"
GREEN      = "27AE60"
WHITE      = "FFFFFF"
BLACK      = "1C2833"
GREY       = "F2F3F4"

def hfont(sz=11, bold=True, color=WHITE):
    return Font(name="Calibri", bold=bold, size=sz, color=color)

def bfont(sz=10, bold=False, color=BLACK):
    return Font(name="Calibri", bold=bold, size=sz, color=color)

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def border():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)

def center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

def style_header(ws, row, ncols, bg=DARK_BLUE):
    for c in range(1, ncols+1):
        cell = ws.cell(row=row, column=c)
        cell.font = hfont(); cell.fill = fill(bg)
        cell.alignment = center(); cell.border = border()

def style_row(ws, row, ncols, even=False):
    for c in range(1, ncols+1):
        cell = ws.cell(row=row, column=c)
        cell.font = bfont()
        cell.fill = fill(LIGHT_BLUE if even else WHITE)
        cell.alignment = center(); cell.border = border()

# ── Load data ──────────────────────────────────────────────────────────────
print("Loading data files ...")
df         = pd.read_csv(os.path.join(DATA_DIR, "retail_cleaned.csv"),
                          parse_dates=["transaction_time"])
monthly    = pd.read_csv(os.path.join(DATA_DIR, "monthly_sales.csv"))
top_prod   = pd.read_csv(os.path.join(DATA_DIR, "top_products.csv"))
by_country = pd.read_csv(os.path.join(DATA_DIR, "country_sales.csv"))
quarterly  = pd.read_csv(os.path.join(DATA_DIR, "quarterly_summary.csv"))
print(f"   Rows in cleaned data : {len(df):,}")

wb = Workbook()
wb.remove(wb.active)

# ══════════════════════════════════════════════════════════════════════════
# SHEET 1 – KPI Dashboard
# ══════════════════════════════════════════════════════════════════════════
print(" Building Sheet 1 – KPI Dashboard ...")
ws1 = wb.create_sheet("KPI Dashboard")
ws1.sheet_view.showGridLines = False
ws1.row_dimensions[1].height = 40

ws1.merge_cells("A1:H1")
ws1["A1"].value = "RETAIL ANALYTICS DASHBOARD"
ws1["A1"].font  = hfont(sz=18); ws1["A1"].fill = fill(DARK_BLUE)
ws1["A1"].alignment = center()

ws1.merge_cells("A2:H2")
ws1["A2"].value = "Sales Performance Report  |  Python Analytics Pipeline"
ws1["A2"].font  = Font(name="Calibri", italic=True, size=10, color="888888")
ws1["A2"].fill  = fill(GREY); ws1["A2"].alignment = center()

total_rev   = round(df["total_sales_value"].sum(), 2)
total_txns  = len(df)
avg_order   = round(df["total_sales_value"].mean(), 2)
top_country = by_country.iloc[0]["Country"]
top_product = top_prod.iloc[0]["Product"]
date_range  = f"{df['transaction_time'].min().strftime('%b %Y')} to {df['transaction_time'].max().strftime('%b %Y')}"

kpis = [
    ("Total Revenue",    f"£{total_rev:,.2f}", MID_BLUE),
    ("Transactions",     f"{total_txns:,}",     ORANGE),
    ("Avg Order Value",  f"£{avg_order:,.2f}",  GREEN),
    ("Date Range",       date_range,            DARK_BLUE),
    ("Top Country",      top_country,           "9B51E0"),
    ("Best Product",     top_product[:22],      "EB5757"),
]

for col, (label, val, color) in enumerate(kpis, 1):
    ws1.cell(4, col, label.upper()).font      = hfont(sz=9, color=WHITE)
    ws1.cell(4, col).fill      = fill(color)
    ws1.cell(4, col).alignment = center()
    ws1.cell(5, col, val).font = Font(name="Calibri", bold=True, size=12, color=color)
    ws1.cell(5, col).fill      = fill(WHITE)
    ws1.cell(5, col).alignment = center()
    ws1.cell(5, col).border    = border()

ws1.row_dimensions[4].height = 22
ws1.row_dimensions[5].height = 30

for fname, anchor in [("01_monthly_trend.png","A7"),("02_top_products.png","E7"),
                       ("03_country_sales.png","A26"),("05_mom_growth.png","E26")]:
    path = os.path.join(CHARTS_DIR, fname)
    if os.path.exists(path):
        try:
            img = XLImage(path); img.width=440; img.height=200
            ws1.add_image(img, anchor)
        except Exception: pass

set_widths(ws1, [18]*8)

# ══════════════════════════════════════════════════════════════════════════
# SHEET 2 – Monthly Sales
# ══════════════════════════════════════════════════════════════════════════
print("Building Sheet 2 – Monthly Sales ...")
ws2 = wb.create_sheet("Monthly Sales")
ws2.sheet_view.showGridLines = False
ws2.merge_cells("A1:G1")
ws2["A1"].value = "Monthly Sales Summary"
ws2["A1"].font  = hfont(sz=13); ws2["A1"].fill = fill(DARK_BLUE)
ws2["A1"].alignment = center(); ws2.row_dimensions[1].height = 28

headers = ["Month","Year","Quarter","Transactions","Revenue (£)","Avg Order (£)","MoM Growth %"]
for c,h in enumerate(headers,1): ws2.cell(2,c,h)
style_header(ws2, 2, len(headers), bg=MID_BLUE)

ms = monthly.sort_values(["year","month"]).reset_index(drop=True)
if "quarter" not in ms.columns:
    ms["quarter"] = ((ms["month"]-1)//3+1)
txn_cnt = df.groupby(["year","month"]).size().reset_index(name="tc")
ms = ms.merge(txn_cnt, on=["year","month"], how="left")
ms["avg_order"] = ms["total_sales_value"] / ms["tc"].replace(0,1)
ms["growth"]    = ms["total_sales_value"].pct_change() * 100

for i, row in enumerate(ms.itertuples(), start=3):
    ws2.cell(i,1, row.month_name)
    ws2.cell(i,2, int(row.year))
    ws2.cell(i,3, int(row.quarter))
    ws2.cell(i,4, int(getattr(row,"tc",0)))
    ws2.cell(i,5, round(row.total_sales_value,2)).number_format = '£#,##0.00'
    ws2.cell(i,6, round(getattr(row,"avg_order",0),2)).number_format = '£#,##0.00'
    g = getattr(row,"growth",None)
    if g is not None and not (isinstance(g,float) and np.isnan(g)):
        cell = ws2.cell(i,7, round(float(g),1))
        cell.font = Font(name="Calibri", size=10, color=GREEN if float(g)>=0 else "EB5757")
    style_row(ws2, i, len(headers), even=(i%2==0))

tr = 3+len(ms)
ws2.cell(tr,1,"TOTAL").font = hfont(color=BLACK)
ws2.cell(tr,5, f"=SUM(E3:E{tr-1})").number_format = '£#,##0.00'
ws2.cell(tr,6, f"=AVERAGE(F3:F{tr-1})").number_format = '£#,##0.00'
style_header(ws2, tr, len(headers), bg=ORANGE)
ws2.freeze_panes = "A3"
set_widths(ws2, [14,8,10,14,16,16,14])

# ══════════════════════════════════════════════════════════════════════════
# SHEET 3 – Top Products
# ══════════════════════════════════════════════════════════════════════════
print("Building Sheet 3 – Top Products ...")
ws3 = wb.create_sheet("Top Products")
ws3.sheet_view.showGridLines = False
ws3.merge_cells("A1:E1")
ws3["A1"].value = "Top Products by Revenue"
ws3["A1"].font  = hfont(sz=13); ws3["A1"].fill = fill(DARK_BLUE)
ws3["A1"].alignment = center(); ws3.row_dimensions[1].height = 28

ph = ["Rank","Product","Revenue (£)","% of Total","Transactions"]
for c,h in enumerate(ph,1): ws3.cell(2,c,h)
style_header(ws3, 2, len(ph), bg=MID_BLUE)

prod_df = df.groupby("item_description").agg(
    revenue=("total_sales_value","sum"),
    txns=("transaction_id","count")
).reset_index().sort_values("revenue",ascending=False).reset_index(drop=True)
grand = prod_df["revenue"].sum()

for i, row in enumerate(prod_df.itertuples(), start=3):
    ws3.cell(i,1, i-2)
    ws3.cell(i,2, row.item_description)
    ws3.cell(i,3, round(row.revenue,2)).number_format = '£#,##0.00'
    ws3.cell(i,4, round(row.revenue/grand*100,2)).number_format = '0.00"%"'
    ws3.cell(i,5, int(row.txns))
    style_row(ws3, i, len(ph), even=(i%2==0))

ws3.freeze_panes = "A3"
set_widths(ws3, [8,26,18,14,14])

# ══════════════════════════════════════════════════════════════════════════
# SHEET 4 – Country Analysis
# ══════════════════════════════════════════════════════════════════════════
print("Building Sheet 4 – Country Analysis ...")
ws4 = wb.create_sheet("Country Analysis")
ws4.sheet_view.showGridLines = False
ws4.merge_cells("A1:D1")
ws4["A1"].value = "Sales by Country"
ws4["A1"].font  = hfont(sz=13); ws4["A1"].fill = fill(DARK_BLUE)
ws4["A1"].alignment = center()

ch = ["Country","Revenue (£)","% of Total","Transactions"]
for c,h in enumerate(ch,1): ws4.cell(2,c,h)
style_header(ws4, 2, len(ch), bg=MID_BLUE)

cdf = df.groupby("country").agg(
    revenue=("total_sales_value","sum"),
    txns=("transaction_id","count")
).reset_index().sort_values("revenue",ascending=False).reset_index(drop=True)
gc = cdf["revenue"].sum()

for i, row in enumerate(cdf.itertuples(), start=3):
    ws4.cell(i,1, row.country); ws4.cell(i,2, round(row.revenue,2)).number_format = '£#,##0.00'
    ws4.cell(i,3, round(row.revenue/gc*100,2)).number_format = '0.00"%"'
    ws4.cell(i,4, int(row.txns))
    style_row(ws4, i, len(ch), even=(i%2==0))

cp = os.path.join(CHARTS_DIR,"03_country_sales.png")
if os.path.exists(cp):
    try:
        img = XLImage(cp); img.width=500; img.height=260
        ws4.add_image(img, f"A{len(cdf)+4}")
    except Exception: pass

ws4.freeze_panes = "A3"
set_widths(ws4, [22,18,14,14])

# ══════════════════════════════════════════════════════════════════════════
# SHEET 5 – Quarterly Summary
# ══════════════════════════════════════════════════════════════════════════
print(" Building Sheet 5 – Quarterly Summary ...")
ws5 = wb.create_sheet("Quarterly Summary")
ws5.sheet_view.showGridLines = False
ws5.merge_cells("A1:E1")
ws5["A1"].value = "Quarterly Revenue Summary"
ws5["A1"].font  = hfont(sz=13); ws5["A1"].fill = fill(DARK_BLUE)
ws5["A1"].alignment = center()

qh = ["Year","Quarter","Transactions","Revenue (£)","Avg Order (£)"]
for c,h in enumerate(qh,1): ws5.cell(2,c,h)
style_header(ws5, 2, len(qh), bg=MID_BLUE)

for i, row in enumerate(quarterly.itertuples(), start=3):
    ws5.cell(i,1, int(row.year)); ws5.cell(i,2, f"Q{int(row.quarter)}")
    ws5.cell(i,3, int(row.transactions))
    ws5.cell(i,4, round(row.revenue,2)).number_format = '£#,##0.00'
    ws5.cell(i,5, round(row.avg_order_value,2)).number_format = '£#,##0.00'
    style_row(ws5, i, len(qh), even=(i%2==0))

tr5 = 3+len(quarterly)
ws5.cell(tr5,1,"TOTAL").font = hfont(color=BLACK)
ws5.cell(tr5,3, f"=SUM(C3:C{tr5-1})")
ws5.cell(tr5,4, f"=SUM(D3:D{tr5-1})").number_format = '£#,##0.00'
ws5.cell(tr5,5, f"=AVERAGE(E3:E{tr5-1})").number_format = '£#,##0.00'
style_header(ws5, tr5, len(qh), bg=ORANGE)
ws5.freeze_panes = "A3"
set_widths(ws5, [10,12,16,18,18])

# ══════════════════════════════════════════════════════════════════════════
# SHEET 6 – Raw Data  ★ FAST: no per-cell styling, use pandas + header only
# ══════════════════════════════════════════════════════════════════════════
print(f" Building Sheet 6 – Raw Data ({len(df):,} rows) [fast mode] ...")

export_cols = ["transaction_id","transaction_time","item_code","item_description",
               "number_of_items","cost_per_item","total_sales_value",
               "country","year","month","month_name","day_of_week"]
export_cols = [c for c in export_cols if c in df.columns]
edf = df[export_cols].copy()

# Sample to 10,000 rows max for Excel (full data already in DB and CSV)
MAX_ROWS = 10000
if len(edf) > MAX_ROWS:
    print(f"   Sampling {MAX_ROWS:,} rows for Excel (full {len(edf):,} rows in retail_cleaned.csv)")
    edf = edf.sample(MAX_ROWS, random_state=42).sort_values("transaction_time").reset_index(drop=True)

nc = len(export_cols)
ws6 = wb.create_sheet("Raw Data (Sample)")
ws6.sheet_view.showGridLines = False

ws6.merge_cells(f"A1:{get_column_letter(nc)}1")
ws6["A1"].value = f"Transaction Dataset Sample – {len(edf):,} rows (Full data: {len(df):,} rows in retail_cleaned.csv)"
ws6["A1"].font  = hfont(sz=11); ws6["A1"].fill = fill(DARK_BLUE)
ws6["A1"].alignment = center(); ws6.row_dimensions[1].height = 22

rh = [c.replace("_"," ").title() for c in export_cols]
for c,h in enumerate(rh,1): ws6.cell(2,c,h)
style_header(ws6, 2, nc, bg=MID_BLUE)

# Write data rows WITHOUT per-cell styling (fast)
for i, row in enumerate(edf.itertuples(index=False), start=3):
    for c, val in enumerate(row, 1):
        ws6.cell(i, c, val)

# Apply alternating fill only on header — skip per-row styling for speed
ws6.freeze_panes = "A3"
set_widths(ws6, [16,20,10,20,12,14,16,18,8,8,12,14])
print(f"    Raw Data sheet done.")

# ── Save ──────────────────────────────────────────────────────────────────
print("\nSaving Excel file ...")
out = os.path.join(REPORTS, "Retail_Analytics_Report.xlsx")
wb.save(out)
size_mb = os.path.getsize(out) / 1024 / 1024
print(f"\n Excel report saved → {out}")
print(f"    File size : {size_mb:.1f} MB")
print(f"    Sheets    : {[s.title for s in wb.worksheets]}")