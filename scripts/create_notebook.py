"""Internal reproducible notebook builder. Normally you only need 01_eda.ipynb."""
from pathlib import Path
import nbformat as nbf
ROOT = Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook()
cells = []

def m(s): cells.append(nbf.v4.new_markdown_cell(s))
def c(s): cells.append(nbf.v4.new_code_cell(s))

m("""# 🎮 Video Game Sales Analytics — Exploratory Data Analysis

**An end-to-end EDA case study**: data audit → cleaning → descriptive statistics → platform and publisher performance → regional comparisons → Nintendo case study → business insights.

**Research question:** What historical patterns emerge across gaming platforms, genres, publishers, and geographic markets?

> **Data model:** Every row represents a **game-platform entry**. `*_Sales` is in **millions of copies**, not dollars. `Year` is the *release* year, and each sales metric is cumulative lifetime units associated with the title; this is **not a dataset of annual transactions**. The sample excludes low-selling releases.""")

m("""## 0. Setup

The notebook works when launched from the repository root or from `notebooks/`. Place your source CSV in `data/games.csv` or run `python scripts/download_data.py` from the project root first.""")
c("""import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path.cwd()
if not (ROOT / 'src').exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

from src.data import load_raw, clean_games, quality_report, REGION_COLUMNS
from src.analysis import (
    category_ranking, filter_games, yearly_trend, region_mix,
    nintendo_japan_genres, nintendo_regional_medians, nintendo_sports_peaks,
)

sns.set_theme(style='whitegrid', palette='muted')
pd.set_option('display.max_columns', 20)
print('Project directory:', ROOT)""")

m("## 1. Data ingestion & basic inspection\nFirst inspect the original source **before deleting rows**. This makes missing-data decisions auditable.")
c("""data_path = ROOT / 'data' / 'games.csv'
if not data_path.exists():
    data_path = ROOT / 'data' / 'vgsales.csv'
raw = load_raw(data_path)
display(raw.head())
print('Rows, columns:', raw.shape)
print('Column dtypes:')
display(raw.dtypes.to_frame('dtype'))""")
c("""missing = raw.isna().sum().sort_values(ascending=False)
display(missing.to_frame('missing_values'))
print('Most missing values in a column:', missing.max())
print('Exact duplicate rows:', raw.duplicated().sum())
print('Rank is an ordinal identifier; names and genres are categorical; year is discrete.')""")

m("## 2. Cleaning and validation\nDrop incomplete observations, invalid sales and exact duplicates. Keep the source untouched and document how many rows were removed.")
c("""games = clean_games(raw)
quality = quality_report(raw, games)
display(pd.DataFrame([quality]).drop(columns=['missing_by_column', 'note']))
print(quality['note'])
assert games.isna().sum().sum() == 0
assert (games[['Global_Sales'] + REGION_COLUMNS] >= 0).all().all()
print('Cleaned shape:', games.shape)""")

m("## 3. Release years — descriptive statistics\nCount **game-platform entries** by release year. Compare mean, median and mode of `Year`.")
c("""display(games['Year'].describe().to_frame('Year'))
print('Mode year(s):', games['Year'].mode().tolist())
print('Mean year:', games['Year'].mean())
print('Median year:', games['Year'].median())
print('Share of records released after 2007: {:.1%}'.format((games['Year'] > 2007).mean()))""")
c("""fig, ax = plt.subplots(figsize=(12, 4))
sns.countplot(data=games, x='Year', order=sorted(games['Year'].unique()), color='#60a5fa', ax=ax)
ax.set(title='Game-platform entries by release year', xlabel='Release year', ylabel='Entry count')
ax.tick_params(axis='x', rotation=90)
plt.tight_layout(); plt.show()""")

m("## 4. Platforms and publishers\nDistinguish **most releases** from **highest lifetime unit sales**. These are different questions.")
c("""platform_share = games['Platform'].value_counts(normalize=True).mul(100)
display(platform_share.loc[platform_share > 7].round(2).rename('share_pct').to_frame())
print('Platforms above 7% of entries:', platform_share.loc[platform_share > 7].index.tolist())
display(category_ranking(games, 'Platform', n=10))
display(category_ranking(games, 'Publisher', n=10))""")
c("""fig, axes = plt.subplots(1, 2, figsize=(15, 6))
platforms = category_ranking(games, 'Platform', n=10)
publishers = category_ranking(games, 'Publisher', n=10)
sns.barplot(data=platforms, y='Platform', x='sales_m', color='#60a5fa', ax=axes[0])
sns.barplot(data=publishers, y='Publisher', x='sales_m', color='#34d399', ax=axes[1])
axes[0].set(title='Top platforms · sales in million copies', xlabel='Million copies', ylabel='')
axes[1].set(title='Top publishers · sales in million copies', xlabel='Million copies', ylabel='')
plt.tight_layout(); plt.show()""")

m("## 5. Geographic market share\nCompare the four regional components. Do **not** include `Global_Sales` as a fifth region — it is a worldwide total.")
c("""mix = region_mix(games)
display(mix.round(2))
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=mix, x='region', y='share_pct', color='#60a5fa', ax=ax)
ax.set(title='Regional share of observed unit sales', xlabel='', ylabel='Share of regional sales, %')
ax.tick_params(axis='x', rotation=15)
plt.tight_layout(); plt.show()""")

m("## 6. Nintendo: regional sales and genre distributions\nCompare *median sales per entry* in NA/EU/JP/Other. For Japan, compare the mean, median and IQR by genre.")
c("""nintendo = games.query("Publisher == 'Nintendo'").copy()
print('Nintendo entries:', len(nintendo))
display(nintendo_regional_medians(games).round(3))
print('Highest Nintendo regional median:', nintendo_regional_medians(games).iloc[0]['region'])
np_stats = nintendo_japan_genres(games)
display(np_stats.round(3))""")
c("""fig, ax = plt.subplots(figsize=(13, 5))
sns.boxplot(data=nintendo, x='Genre', y='JP_Sales', color='#93c5fd', ax=ax)
ax.set(title='Nintendo · Japan unit sales by genre (outliers shown)', xlabel='Genre', ylabel='Million copies')
ax.tick_params(axis='x', rotation=50)
plt.tight_layout(); plt.show()""")

m("## 7. Nintendo five-genre release-year analysis\nCompare `Fighting`, `Simulation`, `Platform`, `Racing`, `Sports` across game release-year cohorts. Summing `Global_Sales` within each cohort shows **lifetime sales of games released in the same year**, not annual sold copies.")
c("""target = ['Fighting', 'Simulation', 'Platform', 'Racing', 'Sports']
five = nintendo[nintendo['Genre'].isin(target)]
genre_cohorts = yearly_trend(five, 'Global_Sales', 'Genre')
display(genre_cohorts.head())
fig, ax = plt.subplots(figsize=(13, 5))
sns.lineplot(data=genre_cohorts, x='Year', y='sales_m', hue='Genre', ax=ax)
ax.set(title='Nintendo: worldwide lifetime units by release-year cohort', ylabel='Million copies', xlabel='Release year')
plt.tight_layout(); plt.show()""")
c("""sports_peaks = nintendo_sports_peaks(games, n=10)
display(sports_peaks)
print('Highest Nintendo Sports release-year cohort:', int(sports_peaks.iloc[0]['Year']))""")

m("## 8. Business interpretation\nThese statements are generated from the data above rather than fixed assumptions. A responsible portfolio analysis should explain what the sample can — and cannot — establish.")
c("""top_platform = category_ranking(games, 'Platform', n=1).iloc[0]
top_publisher = category_ranking(games, 'Publisher', n=1).iloc[0]
top_region = mix.sort_values('sales_m', ascending=False).iloc[0]
print(f"Most recorded cumulative unit sales by platform: {top_platform['Platform']} ({top_platform['sales_m']:.2f}M).")
print(f"Most recorded cumulative unit sales by publisher: {top_publisher['Publisher']} ({top_publisher['sales_m']:.2f}M).")
print(f"Largest observed regional market: {top_region['region']} ({top_region['share_pct']:.1f}% of regional sales).")
print(f"Nintendo's largest Japan genre IQR: {np_stats.iloc[0]['Genre']} ({np_stats.iloc[0]['iqr']:.3f}M).")""")

m("""### Limitations and next steps

1. The source excludes games below the threshold, so platform rankings are **sample rankings**, not a complete industry census.
2. Release-year cohort sales are not sales occurring in that calendar year. **No annual transaction-level forecasts** are justified by these data alone.
3. `Global_Sales` and regional sales measure *copies*, **not money**.
4. Some records share the same game title across multiple platforms.
5. The dataset is historical and does not describe the current market.
6. Dropping incomplete observations introduces a potential selection effect.

**Next steps:** run `streamlit run app.py` for interactive segmentation, `python scripts/generate_report.py` for a written executive summary, and `python scripts/run_sql_analysis.py` for reproducible SQL analysis.

**Source:** Gregory Smith, [Video Games Sales (Zenodo)](https://zenodo.org/records/5898311).""")

nb.cells = cells
nb.metadata = {
  'kernelspec': {'name':'python3', 'display_name':'Python 3', 'language':'python'},
  'language_info': {'name':'python', 'version':'3.11'},
}
path = ROOT / 'notebooks' / '01_eda.ipynb'
nbf.write(nb, path)
print(f'Wrote {len(cells)} notebook cells: {path}')
