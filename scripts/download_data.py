"""Download the public historical VGSales CSV from its archival primary mirror.

Usage: python scripts/download_data.py
Also supports: python scripts/download_data.py --file path/to/games.csv
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "data" / "games.csv"
URLS = [
    "https://zenodo.org/records/5898311/files/vgsales.csv?download=1",
    "https://raw.githubusercontent.com/CodingwithO/VideoGameSales/master/vgsales.csv",
]
REQUIRED = {"Rank", "Name", "Platform", "Year", "Genre", "Publisher", "Global_Sales", "JP_Sales", "EU_Sales", "NA_Sales", "Other_Sales"}


def verify(path: Path) -> int:
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing or len(df) < 100:
        raise ValueError(f"Invalid VGSales file (missing columns: {missing}, rows: {len(df)})")
    return len(df)


def main():
    parser = argparse.ArgumentParser(description="Download VGSales dataset")
    parser.add_argument("--file", type=Path, help="Copy an existing CSV from disk instead of downloading")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing CSV")
    args = parser.parse_args()
    DEFAULT.parent.mkdir(parents=True, exist_ok=True)
    if DEFAULT.exists() and not args.force:
        print(f"Already exists: {DEFAULT} ({verify(DEFAULT):,} records)")
        return
    if args.file:
        import shutil
        shutil.copyfile(args.file, DEFAULT)
        try:
            rows = verify(DEFAULT)
        except Exception:
            DEFAULT.unlink(missing_ok=True)
            raise
        print(f"Copied {rows:,} rows to {DEFAULT}")
        return
    errors = []
    for url in URLS:
        try:
            print(f"Fetching {url}")
            result = requests.get(url, timeout=35, headers={"User-Agent": "VideoGameSalesAnalytics/1.0"})
            result.raise_for_status()
            DEFAULT.write_bytes(result.content)
            rows = verify(DEFAULT)
            print(f"Downloaded {rows:,} records to {DEFAULT}")
            return
        except Exception as exc:
            DEFAULT.unlink(missing_ok=True)
            errors.append(f"{url}: {exc}")
    print("Unable to fetch automatically. Download games.csv from the source and place it in data/.", file=sys.stderr)
    for e in errors:
        print(" - " + e, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
