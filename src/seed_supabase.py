"""
seed_supabase.py
----------------
Reads weekly inference CSVs from data/inference/england/ and upserts
raw articles into the Supabase `articles` table.

Usage (from project root):
    python src/seed_supabase.py                    # seed all weeks
    python src/seed_supabase.py --week 1           # seed a specific week
    python src/seed_supabase.py --dry-run          # print what would be inserted

Credentials are read from .env:
    SUPABASE_URL=https://...supabase.co
    SUPABASE_SERVICE_KEY=sb_secret_...
"""

import argparse
import os
import re
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

ROOT = Path(__file__).resolve().parent.parent
INFERENCE_DIR = ROOT / "data" / "inference" / "england"

# Filename pattern: weekNN_YYYY-MM-DD.csv
FILENAME_RE = re.compile(r"^week(\d+)_(\d{4}-\d{2}-\d{2})\.csv$")


def get_client():
    load_dotenv(ROOT / ".env")
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    return create_client(url, key)


def parse_filename(filename: str):
    """Extract week_number and week_end date from filename."""
    m = FILENAME_RE.match(filename)
    if not m:
        return None, None
    week_number = int(m.group(1))
    week_end = date.fromisoformat(m.group(2))
    week_start = week_end - timedelta(days=6)
    return week_number, week_start, week_end


def seed_file(client, csv_path: Path, dry_run: bool = False):
    filename = csv_path.name
    week_number, week_start, week_end = parse_filename(filename)
    if week_number is None:
        print(f"⚠️  Skipping {filename} — filename doesn't match weekNN_YYYY-MM-DD.csv")
        return 0

    df = pd.read_csv(csv_path)
    df = df.where(pd.notna(df), None)  # replace NaN with None for JSON serialisation

    records = []
    for _, row in df.iterrows():
        record = {
            "url":              row.get("url"),
            "title":            row.get("title"),
            "date":             str(row["date"]) if row.get("date") else None,
            "text":             row.get("text"),
            "source":           row.get("source"),
            "country":          row.get("country"),
            "type":             row.get("type"),
            "institution_name": row.get("institution_name"),
            "week_number":      week_number,
            "week_start":       str(week_start),
            "week_end":         str(week_end),
        }
        if record["url"]:
            records.append(record)

    if not records:
        print(f"⚠️  {filename}: no valid rows (all missing url)")
        return 0

    if dry_run:
        print(f"[dry-run] {filename}: would upsert {len(records)} rows (week {week_number}, {week_start} → {week_end})")
        return len(records)

    # Upsert: on conflict on url, update all columns except url
    result = (
        client.table("articles")
        .upsert(records, on_conflict="url")
        .execute()
    )
    print(f"✅ {filename}: upserted {len(records)} rows (week {week_number}, {week_start} → {week_end})")
    return len(records)


def main():
    parser = argparse.ArgumentParser(description="Seed Supabase articles table from inference CSVs")
    parser.add_argument("--week", type=int, default=None, help="Only seed this week number")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be inserted without writing")
    args = parser.parse_args()

    client = None if args.dry_run else get_client()

    csv_files = sorted(INFERENCE_DIR.glob("week*.csv"))
    if not csv_files:
        print(f"No week*.csv files found in {INFERENCE_DIR}")
        return

    if args.week is not None:
        csv_files = [f for f in csv_files if parse_filename(f.name)[0] == args.week]
        if not csv_files:
            print(f"No file found for week {args.week}")
            return

    total = 0
    for csv_path in csv_files:
        total += seed_file(client, csv_path, dry_run=args.dry_run)

    print(f"\n{'[dry-run] ' if args.dry_run else ''}Total: {total} rows {'would be' if args.dry_run else ''} upserted across {len(csv_files)} file(s)")


if __name__ == "__main__":
    main()
