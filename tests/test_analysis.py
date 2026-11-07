import pytest
from src.data import clean_games
from src.analysis import (
    category_ranking, yearly_trend, nintendo_japan_genres,
    nintendo_regional_medians, nintendo_sports_peaks,
    region_mix, filter_games, platform_genre_matrix,
)


def test_platform_ranking(raw_games):
    games = clean_games(raw_games)
    top = category_ranking(games, "Platform")
    assert top.iloc[0]["Platform"] == "Wii"
    assert top.iloc[0]["sales_m"] == 28.5
    assert top.iloc[0]["releases"] == 2


def test_nintendo_median_and_iqr(raw_games):
    games = clean_games(raw_games)
    japan = nintendo_japan_genres(games).set_index("Genre")
    assert japan.loc["Sports", "median"] == 2.0
    assert japan.loc["Fighting", "median"] == 5.0
    assert japan.loc["Fighting", "iqr"] == 3.0
    medians = nintendo_regional_medians(games)
    assert medians.iloc[0]["region"] == "North America"


def test_year_cohort_aggregation(raw_games):
    games = clean_games(raw_games)
    trend = yearly_trend(games)
    assert trend.set_index("Year").loc[2006, "sales_m"] == 28.5
    peak = nintendo_sports_peaks(games)
    assert int(peak.iloc[0]["Year"]) == 2006
    assert peak.iloc[0]["sales_m"] == 28.5


def test_filter_and_regional_shares(raw_games):
    games = clean_games(raw_games)
    only = filter_games(games, years=(2007, 2007), platforms=["DS"])
    assert len(only) == 2
    share = region_mix(games)
    assert share["share_pct"].sum() == pytest.approx(100.0)
    matrix = platform_genre_matrix(games)
    assert matrix.loc["Wii", "Sports"] == pytest.approx(28.5)
