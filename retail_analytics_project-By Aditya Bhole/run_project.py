"""
run_project.py
--------------
MASTER RUNNER – executes all 4 phases in sequence.
Just run:   python run_project.py
"""

import subprocess, sys, os, time

BASE = os.path.dirname(os.path.abspath(__file__))

PHASES = [
    ("PHASE 1 – Database Setup",          "phase1_db_setup.py"),
    ("PHASE 2 – Data Cleaning",           "phase2_cleaning.py"),
    ("PHASE 3 – Analysis & Charts",       "phase3_analysis.py"),
    ("PHASE 4 – Excel Report",            "phase4_reporting.py"),
]

print("=" * 60)
print("  RETAIL ANALYTICS PROJECT – FULL PIPELINE")
print("=" * 60)

total_start = time.time()
for title, script in PHASES:
    print(f"\n{'─'*60}")
    print(f"▶  {title}")
    print(f"{'─'*60}")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, os.path.join(BASE, script)],
        capture_output=False
    )
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"\n❌  {title} FAILED (exit code {result.returncode})")
        sys.exit(result.returncode)
    print(f"⏱️   Completed in {elapsed:.1f}s")

print(f"\n{'='*60}")
print(f"🎉  ALL PHASES COMPLETE  ({time.time()-total_start:.1f}s total)")
print(f"📁  Find your Excel report at: reports/Retail_Analytics_Report.xlsx")
print(f"📁  Charts in:                 reports/charts/")
print(f"{'='*60}")