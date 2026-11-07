"""Data validation, reproducible cleaning and quality checks.

One observation in VGSales represents a game-platform entry, not a person,
transaction or necessarily a unique game title. All sales are million copies.
"""
from pathlib import Path
import pandas as pd

COLUMNS = [
    "Rank", "Name", "Platform", "Year", "Genre", "Publisher",
    "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales",
]
REGION_COLUMNS = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
SALES_COLUMNS = REGION_COLUMNS + ["Global_Sales"]
CATEGORICAL_COLUMNS = ["Name", "Platform", "Genre", "Publisher"]


def validate_schema(df: pd.DataFrame) -> None:
    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")


def load_raw(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. Run: python scripts/download_data.py "
            "or put games.csv into data/"
        )
    df = pd.read_csv(path)
    validate_schema(df)
    return df


def clean_games(df: pd.DataFrame) -> pd.DataFrame:
    """Drop incomplete/invalid rows, remove exact duplicates and normalize types.

    Intentionally never replace missing years/publishers with guessed values.
    """
    validate_schema(df)
    out = df.loc[:, COLUMNS].copy()
    for name in CATEGORICAL_COLUMNS:
        out[name] = out[name].astype("string").str.strip()
        out[name] = out[name].replace("", pd.NA)
    for name in SALES_COLUMNS + ["Year", "Rank"]:
        out[name] = pd.to_numeric(out[name], errors="coerce")
    out = out.dropna(subset=COLUMNS)
    out = out[(out[SALES_COLUMNS] >= 0).all(axis=1)]
    # Retain source years including future-looking/incorrect entries for transparent review.
    out = out[(out["Year"] == out["Year"].round(0)) & (out["Rank"] == out["Rank"].round(0))]
    out["Year"] = out["Year"].astype(int)
    out["Rank"] = out["Rank"].astype(int)
    return out.drop_duplicates().reset_index(drop=True)


def quality_report(raw: pd.DataFrame, cleaned: pd.DataFrame | None = None) -> dict:
    validate_schema(raw)
    if cleaned is None:
        cleaned = clean_games(raw)
    region_sum = cleaned[REGION_COLUMNS].sum(axis=1)
    diff = (cleaned["Global_Sales"] - region_sum).abs()
    return {
        "source_rows": int(len(raw)),
        "clean_rows": int(len(cleaned)),
        "removed_rows": int(len(raw) - len(cleaned)),
        "missing_by_column": {k: int(v) for k, v in raw[COLUMNS].isna().sum().items()},
        "exact_duplicate_rows": int(raw.duplicated().sum()),
        "regional_sum_difference_max_m": float(diff.max()) if len(diff) else 0.0,
        "regional_sum_difference_gt_0_05_count": int((diff > 0.05).sum()),
        "note": "Source sales are rounded; regional totals need not match worldwide values exactly.",
    }
