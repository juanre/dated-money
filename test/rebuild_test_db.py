#!/usr/bin/env python3
"""Add test rates from JSON files to existing database."""
import json
import os
import sqlite3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dated_money.rates import cache_day_rates

# Set test database location
os.environ["DMON_RATES_CACHE"] = str(Path(__file__).parent / "res")

# First, check what dates we already have
db_path = Path(__file__).parent / "res" / "exchange-rates.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT date FROM rates ORDER BY date")
existing_dates = [row[0] for row in cursor.fetchall()]
conn.close()

print(f"Database currently has {len(existing_dates)} dates:")
for date in existing_dates:
    print(f"  {date}")

# Read and cache each JSON file
json_dir = Path(__file__).parent / "res" / "money"
added_count = 0
for json_file in sorted(json_dir.glob("*-rates.json")):
    date_str = json_file.stem.replace("-rates", "")

    if date_str in existing_dates:
        print(f"Skipping {date_str} - already in database")
        continue

    print(f"Adding rates for {date_str}...")

    with open(json_file) as f:
        data = json.load(f)
        rates = data["conversion_rates"]
        cache_day_rates(date_str, rates)
        added_count += 1

print(f"\nDone! Added {added_count} new dates to the database.")
