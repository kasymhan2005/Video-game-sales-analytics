"""Business-facing aggregations used by dashboard, notebook and reports."""
from __future__ import annotations
import pandas as pd
from src.data import REGION_COLUMNS

REGIONS = {
    "North America": "NA_Sales", "Europe": "EU_Sales",
    "Japan": "JP_Sales", "Other regions": "Other_Sales",
    "Worldwide": "Global_Sales",
}
NINTENDO_GENRES = ["Fighting", "Simulation", "Platform", "Racing", "Sports"]


def filter_games(
    df: pd.DataFrame, years: tuple[int, int] | None = None,
    platforms: list[str] | None = None,
    genres: list[str] | None = None,
    publishers: list[str] | None = None,
) -> pd.DataFrame:
    result = df
    if years is not None:
        result = result[result["Year"].between(*years)]
    for field, chosen in [("Platform", platforms), ("Genre", genres), ("Publisher", publishers)]:
        if chosen is not None:
            result = result[result[field].isin(chosen)]
    return result.copy()


def category_ranking(df: pd.DataFrame, category: str, metric: str = "Global_Sales", n: int = 10) -> pd.DataFrame:
    if category not in {"Platform", "Genre", "Publisher"}:
        raise ValueError("Unsupported category")
    if metric not in list(REGIONS.values()):
        raise ValueError("Unsupported sales metric")
    if df.empty:
        return pd.DataFrame(columns=[category, "sales_m", "releases"])
    agg = df.groupby(category, observed=True).agg(
        sales_m=(metric, "sum"), releases=("Rank", "size")
    ).sort_values("sales_m", ascending=False)
    return agg.head(n).reset_index()


def yearly_trend(df: pd.DataFrame, metric: str = "Global_Sales", segment: str | None = None) -> pd.DataFrame:
    if metric not in list(REGIONS.values()):
        raise ValueError("Unsupported sales metric")
    fields = ["Year"] + ([segment] if segment in {"Genre", "Platform", "Publisher"} else [])
    if df.empty:
        return pd.DataFrame(columns=fields + ["sales_m"])
    return (
        df.groupby(fields, as_index=False, observed=True)[metric]
        .sum().rename(columns={metric: "sales_m"}).sort_values(fields)
    )


def region_mix(df: pd.DataFrame) -> pd.DataFrame:
    total = df[REGION_COLUMNS].sum()
    result = total.rename_axis("column").reset_index(name="sales_m")
    result["region"] = result["column"].map({v: k for k, v in REGIONS.items()})
    denominator = result["sales_m"].sum()
    result["share_pct"] = 100 * result["sales_m"] / denominator if denominator > 0 else 0.0
    return result[["region", "sales_m", "share_pct"]]


def nintendo_japan_genres(df: pd.DataFrame) -> pd.DataFrame:
    nintendo = df[df["Publisher"].eq("Nintendo")]
    grouped = nintendo.groupby("Genre", observed=True)["JP_Sales"]
    if nintendo.empty:
        return pd.DataFrame(columns=["Genre", "count", "mean", "median", "q1", "q3", "iqr"])
    stats = grouped.agg(count="count", mean="mean", median="median").reset_index()
    quartiles = grouped.quantile([0.25, 0.75]).unstack().reset_index()
    quartiles = quartiles.rename(columns={0.25: "q1", 0.75: "q3"})
    result = stats.merge(quartiles, on="Genre")
    result["iqr"] = result["q3"] - result["q1"]
    return result.sort_values("iqr", ascending=False).reset_index(drop=True)


def nintendo_regional_medians(df: pd.DataFrame) -> pd.DataFrame:
    n = df.loc[df["Publisher"].eq("Nintendo"), REGION_COLUMNS]
    medians = n.median().rename_axis("column").reset_index(name="median_m")
    medians["region"] = medians["column"].map({v: k for k, v in REGIONS.items()})
    return medians[["region", "median_m"]].sort_values("median_m", ascending=False)


def nintendo_sports_peaks(df: pd.DataFrame, n: int = 7) -> pd.DataFrame:
    games = df[df["Publisher"].eq("Nintendo") & df["Genre"].eq("Sports")]
    return yearly_trend(games).nlargest(n, "sales_m").reset_index(drop=True)


def platform_genre_matrix(df: pd.DataFrame, metric: str = "Global_Sales", top_n: int = 10) -> pd.DataFrame:
    top = category_ranking(df, "Platform", metric, n=top_n)["Platform"].tolist()
    subset = df[df["Platform"].isin(top)]
    if subset.empty:
        return pd.DataFrame()
    return subset.pivot_table(index="Platform", columns="Genre", values=metric, aggfunc="sum", fill_value=0)
