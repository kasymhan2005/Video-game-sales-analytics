"""Interactive Streamlit dashboard. Run: streamlit run app.py"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from src.analysis import (
    REGIONS, NINTENDO_GENRES, category_ranking, filter_games,
    nintendo_japan_genres, nintendo_regional_medians, nintendo_sports_peaks,
    platform_genre_matrix, region_mix, yearly_trend,
)
from src.charts import PALETTE, box_plot, donut_mix, heatmap, horizontal_ranking, style, trend_line
from src.data import REGION_COLUMNS, clean_games, load_raw, quality_report

st.set_page_config(page_title="Video Game Sales | Market Intelligence", page_icon="🎮", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1450px;}
.titleline {font-size: .78rem; letter-spacing: .18em; color: #60a5fa; font-weight: 700;}
.subtitle {font-size: 1.03rem; color: #9cb2d1; margin: -.2rem 0 1.3rem;}
[data-testid="stMetric"] {background:#17243a; padding:16px 18px; border: 1px solid #273955; border-radius: 14px;}
[data-testid="stMetricLabel"] {color:#a7bedc;}
[data-testid="stMetricValue"] {font-size:1.85rem;}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).resolve().parent
FILES = [ROOT / "data" / "games.csv", ROOT / "data" / "vgsales.csv"]

@st.cache_data(show_spinner=False)
def prepare(path: str, mtime: float) -> tuple[pd.DataFrame, dict]:
    raw = load_raw(path)
    clean = clean_games(raw)
    return clean, quality_report(raw, clean)

st.sidebar.markdown("### 🎮 Market intelligence")
st.sidebar.caption("Historical VGSales • game/platform records")
upload = st.sidebar.file_uploader("Or upload your games.csv", type=["csv"])
source = next((p for p in FILES if p.exists()), None)
if upload is not None:
    try:
        raw_df = pd.read_csv(upload)
        games = clean_games(raw_df)
        audit = quality_report(raw_df, games)
    except Exception as exc:
        st.error(f"Invalid uploaded dataset: {exc}")
        st.stop()
elif source is not None:
    try:
        games, audit = prepare(str(source), source.stat().st_mtime)
    except Exception as exc:
        st.error(f"Cannot load CSV: {exc}")
        st.stop()
else:
    st.title("🎮 Video Game Sales Analytics")
    st.warning("Dataset not found. Download it before starting the dashboard, or upload it from the sidebar.")
    st.code("python scripts/download_data.py\nstreamlit run app.py", language="bash")
    st.markdown("[Source dataset on Zenodo](https://zenodo.org/records/5898311) · [Course mirror on Yandex Disk](https://disk.360.yandex.ru/i/eQEYbmT4YSCUHQ)")
    st.stop()

if games.empty:
    st.error("The data file contains no valid rows after cleaning.")
    st.stop()

st.sidebar.divider()
min_year, max_year = int(games["Year"].min()), int(games["Year"].max())
year_range = st.sidebar.slider("Release year", min_year, max_year, (min_year, max_year))
metric_label = st.sidebar.selectbox("Sales region", list(REGIONS), index=4)
metric = REGIONS[metric_label]
selected_platforms = st.sidebar.multiselect("Platforms", sorted(games["Platform"].unique()))
selected_genres = st.sidebar.multiselect("Genres", sorted(games["Genre"].unique()))
selected_publishers = st.sidebar.multiselect("Publishers", sorted(games["Publisher"].unique()))
filtered = filter_games(games, year_range, selected_platforms or None, selected_genres or None, selected_publishers or None)
st.sidebar.caption("Empty filter = all categories. All figures update from the current selection.")

st.markdown('<div class="titleline">INTERACTIVE DATA PORTFOLIO · HISTORICAL MARKET VIEW</div>', unsafe_allow_html=True)
st.title("🎮 Video Game Sales Analytics")
st.markdown('<div class="subtitle">Explore game releases, estimated lifetime unit sales, platform performance, genre patterns and regional differences.</div>', unsafe_allow_html=True)

if filtered.empty:
    st.info("No games match these filters. Broaden the selection in the sidebar.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric(f"{metric_label} sales", f"{filtered[metric].sum():,.1f}M", help="Million copies, summed across selected game-platform records")
k2.metric("Game-platform entries", f"{len(filtered):,}", help="Not necessarily unique game titles")
k3.metric("Platforms", f"{filtered['Platform'].nunique():,}")
k4.metric("Publishers", f"{filtered['Publisher'].nunique():,}")

(tab1, tab2, tab3, tab4, tab5) = st.tabs([
    "📊 Overview", "📈 Release-year trends", "🌍 Regional markets", "🍄 Nintendo deep dive", "📚 Data & methods"
])

with tab1:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(horizontal_ranking(category_ranking(filtered, "Platform", metric), "Platform", "Top platforms by unit sales"), use_container_width=True)
    with right:
        st.plotly_chart(horizontal_ranking(category_ranking(filtered, "Genre", metric), "Genre", "Top genres by unit sales"), use_container_width=True)
    l2, r2 = st.columns([1, 1])
    with l2:
        st.plotly_chart(horizontal_ranking(category_ranking(filtered, "Publisher", metric, n=10), "Publisher", "Top publishers by unit sales"), use_container_width=True)
    with r2:
        st.subheader("Top game-platform records")
        top = filtered.nlargest(12, metric)[["Name", "Platform", "Year", "Genre", "Publisher", metric]].copy()
        st.dataframe(top.rename(columns={metric: f"{metric_label} sales (M)"}), use_container_width=True, hide_index=True)
    with st.expander("Interpret the rankings"):
        st.write("Sales charts sum **estimated lifetime unit sales** for game-platform entries released within the selected range. The same game can appear on multiple platforms; sales are not annual transactions.")

with tab2:
    st.plotly_chart(trend_line(yearly_trend(filtered, metric), f"{metric_label}: sales of games grouped by release year"), use_container_width=True)
    st.caption("X-axis = game release year. Y-axis = cumulative sales of titles released that year, *not sales during that calendar year*.")
    breakdown = st.radio("Compare release-year cohorts by", ["Genre", "Platform", "Publisher"], horizontal=True)
    highest = category_ranking(filtered, breakdown, metric, n=5)[breakdown].tolist()
    candidates = filtered[filtered[breakdown].isin(highest)]
    st.plotly_chart(trend_line(yearly_trend(candidates, metric, breakdown), f"Top 5 {breakdown.lower()} categories over release cohorts", breakdown), use_container_width=True)
    releases = filtered.groupby("Year").size().reset_index(name="releases")
    fig = px.bar(releases, x="Year", y="releases", title="Number of game-platform releases by year", color_discrete_sequence=[PALETTE[1]], labels={"releases": "Game-platform entries"})
    st.plotly_chart(style(fig, 350), use_container_width=True)

with tab3:
    a, b = st.columns([1, 1.5])
    mix = region_mix(filtered)
    with a:
        st.plotly_chart(donut_mix(mix), use_container_width=True)
    with b:
        st.subheader("Regional performance")
        st.dataframe(mix.round(2), use_container_width=True, hide_index=True)
        lead = mix.loc[mix["sales_m"].idxmax()]
        st.info(f"Largest cumulative regional sales: **{lead['region']}** ({lead['share_pct']:.1f}% of regional sales).")
        st.caption("The four regional components approximately sum to worldwide sales. Small differences arise from rounding in the source.")
    long = filtered.groupby("Year", as_index=False)[REGION_COLUMNS].sum().melt(id_vars="Year", var_name="Region", value_name="sales_m")
    long["Region"] = long["Region"].map({"NA_Sales": "North America", "EU_Sales": "Europe", "JP_Sales": "Japan", "Other_Sales": "Other regions"})
    fig = px.area(long, x="Year", y="sales_m", color="Region", title="Regional sales by release-year cohort", color_discrete_sequence=PALETTE, labels={"sales_m": "Million copies", "Year": "Release year"})
    st.plotly_chart(style(fig, 440), use_container_width=True)
    matrix = platform_genre_matrix(filtered, metric)
    if not matrix.empty:
        st.plotly_chart(heatmap(matrix), use_container_width=True)

with tab4:
    # This deep dive always compares Nintendo, regardless of the global publisher filter.
    n_scope = filter_games(games, year_range, selected_platforms or None, selected_genres or None)
    nintendo = n_scope[n_scope["Publisher"].eq("Nintendo")]
    st.caption("Nintendo view respects year, platform and genre filters, but intentionally ignores the sidebar publisher filter.")
    if nintendo.empty:
        st.info("No Nintendo records match the selected years/platforms/genres.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Nintendo entries", f"{len(nintendo):,}")
        c2.metric("Nintendo worldwide", f"{nintendo['Global_Sales'].sum():,.1f}M")
        median_region = nintendo_regional_medians(n_scope).iloc[0]
        c3.metric("Highest regional median", str(median_region["region"]))
        b1, b2 = st.columns([1.5, 1])
        with b1:
            st.plotly_chart(box_plot(nintendo), use_container_width=True)
        with b2:
            st.subheader("Japan sales: genre statistics")
            st.caption("IQR = 75th percentile − 25th percentile; all sales in million copies")
            stat = nintendo_japan_genres(n_scope)
            st.dataframe(stat[["Genre", "count", "mean", "median", "iqr"]].round(3), use_container_width=True, hide_index=True)
        ng = nintendo[nintendo["Genre"].isin(NINTENDO_GENRES)]
        if not ng.empty:
            st.plotly_chart(trend_line(yearly_trend(ng, "Global_Sales", "Genre"), "Nintendo: selected genre sales by release year", "Genre"), use_container_width=True)
        peaks = nintendo_sports_peaks(n_scope)
        if not peaks.empty:
            st.markdown("**Strongest Nintendo Sports release-year cohorts**")
            st.dataframe(peaks.rename(columns={"sales_m": "Global sales (M)"}), hide_index=True, use_container_width=True)

with tab5:
    st.subheader("Cleaning & data quality")
    st.json(audit, expanded=False)
    st.markdown("""
    **Unit:** million physical game copies (estimated), not dollars. **Grain:** one game-platform record.
    This is a historical, selected sample (games above roughly 100,000 copies). It is **not** complete coverage of all games.
    The dataset's `Year` is a game release year; `Global_Sales` is cumulative sales associated with that title.
    Consequently, yearly lines represent *release cohorts*, not total industry revenue or sales in a calendar year.

    **Cleaning:** remove incomplete or invalid rows (no imputation); normalize numeric fields; remove exact duplicates.
    Source rounding may mean that four regional values do not exactly equal worldwide sales. A reported 0.00 may reflect rounding.
    """)
    st.markdown("[Original dataset on Zenodo](https://zenodo.org/records/5898311) · [Original Kaggle listing](https://www.kaggle.com/datasets/gregorut/videogamesales)")
    st.download_button("Download filtered data as CSV", filtered.to_csv(index=False).encode("utf-8"), file_name="filtered_games.csv", mime="text/csv")

st.caption("Portfolio project · pandas / Plotly / Streamlit · Source: Gregory Smith's historical VGSales dataset")
