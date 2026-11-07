"""Reproducible markdown insight report and publication-ready charts.

Run from repository root: python scripts/generate_report.py
"""
from __future__ import annotations
from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import load_raw, clean_games, quality_report
from src.analysis import category_ranking, nintendo_japan_genres, nintendo_regional_medians, nintendo_sports_peaks, region_mix, yearly_trend

DATA = next((x for x in (ROOT / "data" / "games.csv", ROOT / "data" / "vgsales.csv") if x.exists()), ROOT / "data" / "games.csv")
OUT = ROOT / "reports"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def save(name):
    plt.tight_layout()
    plt.savefig(FIG / name, dpi=170, facecolor="white", bbox_inches="tight")
    plt.close()


def fmt_table(df, cols=None, fmt=".2f"):
    """Simple zero-dependency markdown table, stable across pandas versions."""
    if cols:
        df = df.loc[:, cols]
    cols = list(df.columns)
    header = "| " + " | ".join(map(str, cols)) + " |"
    line = "| " + " | ".join("---" for _ in cols) + " |"
    rows = []
    for row in df.itertuples(index=False, name=None):
        cells = [(f"{x:{fmt}}" if isinstance(x, float) else str(x)).replace("|", "/") for x in row]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, line] + rows)


def main():
    raw = load_raw(DATA)
    games = clean_games(raw)
    audit = quality_report(raw, games)
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams.update({"figure.figsize": (10, 5), "axes.titleweight": "bold", "font.size": 11})

    platforms = category_ranking(games, "Platform", n=10)
    plt.figure()
    sns.barplot(data=platforms, x="sales_m", y="Platform", color="#2563eb")
    plt.title("Top platforms · cumulative worldwide unit sales")
    plt.xlabel("Million copies"); plt.ylabel("")
    save("platforms.png")

    years = yearly_trend(games)
    plt.figure()
    sns.lineplot(data=years, x="Year", y="sales_m", color="#2563eb", linewidth=2.2)
    plt.title("Lifetime sales by game release-year cohort")
    plt.xlabel("Release year"); plt.ylabel("Million copies")
    save("release_cohorts.png")

    nintendo = games[games["Publisher"].eq("Nintendo")].copy()
    plt.figure(figsize=(13, 6))
    sns.boxplot(data=nintendo, x="Genre", y="JP_Sales", showfliers=False, color="#93c5fd")
    plt.xticks(rotation=45, ha="right"); plt.ylabel("Japan sales (million copies)")
    plt.title("Nintendo Japan unit sales by genre · outliers hidden for readability")
    save("nintendo_japan_boxplot.png")

    # Nintendo cohort trends — five genres from the original analysis question.
    five_genres = ["Fighting", "Simulation", "Platform", "Racing", "Sports"]
    subset = nintendo[nintendo["Genre"].isin(five_genres)]
    genre_cohorts = yearly_trend(subset, segment="Genre")
    plt.figure(figsize=(12, 5.5))
    sns.lineplot(data=genre_cohorts, x="Year", y="sales_m", hue="Genre", linewidth=2.3)
    plt.title("Nintendo: lifetime unit sales by game release-year cohort")
    plt.xlabel("Release year"); plt.ylabel("Million copies")
    plt.legend(title="Genre", ncol=5, loc="upper center", bbox_to_anchor=(.5, -.16))
    save("nintendo_genre_cohorts.png")

    # Regional market composition (four regional components only).
    regional = region_mix(games)
    plt.figure(figsize=(9.5, 5))
    sns.barplot(data=regional, x="region", y="share_pct", color="#2563eb")
    plt.title("Observed unit sales share by region")
    plt.xlabel(""); plt.ylabel("Share of regional unit sales (%)")
    save("regional_mix.png")

    peak = nintendo_sports_peaks(games, n=7)
    jp = nintendo_japan_genres(games)
    med = nintendo_regional_medians(games)
    regions = region_mix(games)
    top_publisher = category_ranking(games, "Publisher", n=1).iloc[0]
    top_platform = platforms.iloc[0]
    peak_year = years.loc[years["sales_m"].idxmax()]

    body = f"""# Video Game Sales — Analytical Findings

> Auto-generated from `{DATA.name}` by `python scripts/generate_report.py`. All displayed results are calculated from the file at runtime.

## Executive summary

- **{len(games):,}** valid game-platform observations from **{len(raw):,}** source rows. **{audit['removed_rows']:,}** rows removed during cleaning.
- **{games['Global_Sales'].sum():,.2f} million** cumulative worldwide copies across observations (dataset estimate).
- Leading platform by *cumulative worldwide copies*: **{top_platform['Platform']}** ({top_platform['sales_m']:,.2f} million).
- Leading publisher by *cumulative worldwide copies*: **{top_publisher['Publisher']}** ({top_publisher['sales_m']:,.2f} million).
- Release-year cohort with greatest accumulated unit sales: **{int(peak_year['Year'])}** ({peak_year['sales_m']:,.2f} million).
- **{len(nintendo):,}** Nintendo-published game-platform records in the cleaned dataset.

## 1. Data quality

| Metric | Result |
| --- | ---: |
| Raw rows | {len(raw):,} |
| Clean rows | {len(games):,} |
| Removed rows | {audit['removed_rows']:,} |
| Missing Year in raw source | {audit['missing_by_column']['Year']:,} |
| Missing Publisher in raw source | {audit['missing_by_column']['Publisher']:,} |
| Duplicate source rows | {audit['exact_duplicate_rows']:,} |
| Maximum regional sum vs worldwide absolute discrepancy | {audit['regional_sum_difference_max_m']:.3f} million |

We remove missing or invalid observations rather than invent release years or publishers. Regional/worldwide fields are rounded in the original data.

## 2. Historical platform performance

{fmt_table(platforms[['Platform','sales_m','releases']])}

![Top platforms](figures/platforms.png)

## 3. Release-year cohorts

The most commercially successful release cohort, measured by lifetime copies of games **released that year**, is {int(peak_year['Year'])}. This is not an estimate of sales that occurred in that calendar year.

![Release-year cohorts](figures/release_cohorts.png)

## 4. Regional distribution

{fmt_table(regions)}

![Regional unit shares](figures/regional_mix.png)

These percentages divide the sum of the four regional sales estimates; rounding may cause small differences from `Global_Sales`.

## 5. Nintendo: Japan, genre, and release cohorts

Highest Nintendo **regional median sales per record** (not sum): **{med.iloc[0]['region']}**, {med.iloc[0]['median_m']:.3f} million copies.

{fmt_table(med)}

Japan unit sales by genre, including the interquartile range (IQR):

{fmt_table(jp[['Genre','count','mean','median','iqr']])}

![Nintendo Japan by genre](figures/nintendo_japan_boxplot.png)

Five Nintendo genres over release-year cohorts (cumulative lifetime copies of games **released** in each year):

![Nintendo genre cohorts](figures/nintendo_genre_cohorts.png)

Nintendo Sports release-year cohorts with highest lifetime worldwide unit sales:

{fmt_table(peak.rename(columns={'sales_m':'Global sales (M)'}) )}

## 6. Responsible interpretation

1. **Selection bias:** source includes only games exceeding roughly 100,000 copies; less successful releases are not represented.
2. **Temporal interpretation:** sales are associated with each game's release year, but are accumulated over its lifetime up to the dataset capture, not annual transaction-level sales.
3. **Sample coverage:** observations are game-platform pairs. Never interpret them as unique game titles without deduplicating `Name`.
4. **Measurement:** `*_Sales` means *million units/copies*, **not revenue** or US dollars.
5. **Age of data:** suitable for historical study, not for 2026 market forecasts.
6. **Outliers and skew:** mean and median may differ; IQR and boxplots help compare distributions.
7. **Rounding:** small discrepancies between regional and worldwide sums are expected.

## Reproduce

```bash
python scripts/download_data.py
python scripts/generate_report.py
streamlit run app.py
```

Dataset: Gregory Smith (2016), archival copy at https://zenodo.org/records/5898311 .
"""
    (OUT / "insights.md").write_text(body, encoding="utf-8")
    print(f"Wrote {OUT / 'insights.md'} and 5 PNG charts")
    print(f"Sample: {len(raw):,} source / {len(games):,} cleaned rows")


if __name__ == "__main__":
    main()
