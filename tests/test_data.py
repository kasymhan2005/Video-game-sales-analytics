import pandas as pd
import pytest
from src.data import clean_games, quality_report, validate_schema


def test_clean_preserves_grain_and_casts_year(raw_games):
    result = clean_games(raw_games)
    assert len(result) == 6
    assert pd.api.types.is_integer_dtype(result["Year"])
    assert result["Publisher"].nunique() == 2


def test_clean_drops_null_negative_and_exact_duplicate(raw_games):
    modified = raw_games.copy()
    modified.loc[0, "Year"] = None
    modified.loc[1, "JP_Sales"] = -1
    modified = pd.concat([modified, modified.iloc[[2]]], ignore_index=True)
    result = clean_games(modified)
    assert len(result) == 4
    audit = quality_report(modified, result)
    assert audit["removed_rows"] == 3
    assert audit["missing_by_column"]["Year"] == 1


def test_required_columns_detected(raw_games):
    with pytest.raises(ValueError, match="Global_Sales"):
        validate_schema(raw_games.drop(columns=["Global_Sales"]))
