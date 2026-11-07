"""Load cleaned rows into SQLite and export results of sql/analysis.sql.

Usage: python scripts/run_sql_analysis.py
"""
from pathlib import Path
import sqlite3
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import load_raw, clean_games


def main():
    dataset = next((p for p in (ROOT / "data" / "games.csv", ROOT / "data" / "vgsales.csv") if p.exists()), ROOT / "data" / "games.csv")
    games = clean_games(load_raw(dataset))
    conn = sqlite3.connect(":memory:")
    try:
        games.to_sql("games", conn, index=False)
        sql = (ROOT / "sql" / "analysis.sql").read_text(encoding="utf-8")
        queries = [q.strip() for q in sql.split(";") if q.strip()]
        lines = ["# SQL Analysis Results", "", "Generated from cleaned local VGSales data.", ""]
        for n, query in enumerate(queries, 1):
            result = pd.read_sql_query(query, conn)
            lines += [f"## Query {n}", "", "```sql", query, "```", "", "```text", result.to_string(index=False), "```", ""]
        output = ROOT / "reports" / "sql_results.md"
        output.write_text("\n".join(lines), encoding="utf-8")
        print(f"Executed {len(queries)} queries; saved {output}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
