# Merges the per-source CSVs from data/training/ into a versioned training_data_vN.csv.
# Run this after all source scrapers have completed (Mode A / retrospective only).
#
# Usage:
#   python merge.py              → outputs training_data_v2.csv (increment manually)
#   python merge.py --version 2  → outputs training_data_v2.csv
#
# Currently merges England-only sources.
# Phase 2: add Scotland and Ireland sources here to retrain cross-jurisdiction.

import argparse
import pandas as pd
from pathlib import Path
from datetime import date

TRAINING_CUTOFF = date(2025, 12, 31)  # must match run.py

ROOT = Path(__file__).resolve().parents[1]
TRAINING = ROOT / "data" / "training"
ENG = TRAINING / "england"

SOURCES = {
    "schoolsweek": {
        "file": ENG / "schoolsweek.csv",
        "country": "eng",
        "type": "ed_journalism",
        "institution_name": "Schools Week",
    },
    "epi": {
        "file": ENG / "epi.csv",
        "country": "eng",
        "type": "think_tank",
        "institution_name": "Education Policy Institute",
    },
    "nuffield": {
        "file": ENG / "nuffield.csv",
        "country": "eng",
        "type": "think_tank",
        "institution_name": "Nuffield Foundation",
    },
    "fft": {
        "file": ENG / "fft_education_datalab.csv",
        "country": "eng",
        "type": "ed_res_org",
        "institution_name": "FFT Education Datalab",
    },
    "fed": {
        "file": ENG / "fed.csv",
        "country": "eng",
        "type": "prof_body",
        "institution_name": "Foundation for Educational Development",
    },
}

GOV_FILE = ENG / "govuk_education.csv"
FINAL_COLS = ["url", "title", "date", "text", "source", "country", "type", "institution_name"]


def load_standard(source, config):
    df = pd.read_csv(config["file"])
    df["source"] = source
    df["country"] = config["country"]
    df["type"] = config["type"]
    df["institution_name"] = config["institution_name"]

    # SchoolsWeek dates include a timestamp — strip to date only
    if source == "schoolsweek":
        df["date"] = df["date"].astype(str).str.split(" ").str[0]

    # Drop rows with missing or empty text
    df = df.dropna(subset=["text"])
    df = df[df["text"].str.strip() != ""]

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df[FINAL_COLS]


def load_gov():
    df = pd.read_csv(GOV_FILE)

    # Keep only core education bodies
    df = df[df["core_education"] == True].copy()

    df["source"] = "gov"
    df["country"] = "eng"
    df["type"] = "government"
    df["institution_name"] = df["primary_org"]

    df = df.dropna(subset=["text"])
    df = df[df["text"].str.strip() != ""]

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df[FINAL_COLS]


def parse_args():
    parser = argparse.ArgumentParser(description="Merge per-source training CSVs")
    parser.add_argument(
        "--version", type=int, default=2,
        help="Version number for output file (e.g. 2 → training_data_v2.csv)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    frames = []

    for source, config in SOURCES.items():
        if not config["file"].exists():
            print(f"⚠️  Missing: {config['file'].name} — skipping")
            continue
        df = load_standard(source, config)
        print(f"✅ {source}: {len(df)} rows")
        frames.append(df)

    if GOV_FILE.exists():
        df = load_gov()
        print(f"✅ gov: {len(df)} rows")
        frames.append(df)
    else:
        print(f"⚠️  Missing: {GOV_FILE.name} — skipping")

    if not frames:
        print("❌ No source files found. Exiting.")
        return

    full = pd.concat(frames, ignore_index=True)
    full["date"] = pd.to_datetime(full["date"], errors="coerce")

    # Cap at training cutoff — exclude anything scraped beyond Dec 2025
    before_cap = len(full)
    full = full[full["date"] <= pd.Timestamp(TRAINING_CUTOFF)]
    capped = before_cap - len(full)
    if capped:
        print(f"✂️  Excluded {capped} articles after {TRAINING_CUTOFF} (outside training window)")

    # Drop duplicate URLs (can arise from top-up append runs)
    before = len(full)
    full = full.drop_duplicates(subset=["url"])
    dupes = before - len(full)
    if dupes:
        print(f"🧹 Dropped {dupes} duplicate rows")

    TRAINING.mkdir(parents=True, exist_ok=True)
    out = TRAINING / f"training_data_v{args.version}.csv"
    full.to_csv(out, index=False)

    print(f"\n✅ Wrote {len(full)} rows to {out}")
    print(full["source"].value_counts().to_string())


if __name__ == "__main__":
    main()
