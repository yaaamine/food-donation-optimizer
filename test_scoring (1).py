"""
Unit tests for the scoring module.

Run with:
    python -m pytest tests/ -v
"""

import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scoring import compute_score, normalize, validate_data, generate_recommendation


def simple_dataset() -> pd.DataFrame:
    """Two regions with opposite profiles, to check the direction of the ranking."""
    return pd.DataFrame({
        "region": ["Critical_Region", "Comfortable_Region"],
        "population": [1_000_000, 1_000_000],
        "food_insecurity_rate_pct": [30.0, 5.0],   # critical = very high
        "distance_to_hub_km": [500, 50],            # critical = far
        "stock_on_hand_tonnes": [5, 200],           # critical = low stock
        "days_until_expiry": [2, 30],                # critical = close to expiry
    })


def test_validate_data_ok():
    df = simple_dataset()
    validate_data(df)  # must not raise any exception


def test_validate_data_missing_column():
    df = simple_dataset().drop(columns=["distance_to_hub_km"])
    with pytest.raises(ValueError, match="Missing columns"):
        validate_data(df)


def test_validate_data_negative_value():
    df = simple_dataset()
    df.loc[0, "stock_on_hand_tonnes"] = -10
    with pytest.raises(ValueError, match="negative"):
        validate_data(df)


def test_normalize_min_max():
    series = pd.Series([0, 5, 10])
    result = normalize(series)
    assert result.iloc[0] == 0.0
    assert result.iloc[2] == 1.0
    assert result.iloc[1] == 0.5


def test_normalize_identical_values():
    """If all values are equal, no division by zero: returns 0.5 everywhere."""
    series = pd.Series([7, 7, 7])
    result = normalize(series)
    assert (result == 0.5).all()


def test_compute_score_logical_order():
    """The most struggling region on every criterion must come out first."""
    df = simple_dataset()
    result = compute_score(df)
    assert result.iloc[0]["region"] == "Critical_Region"
    assert result.iloc[0]["priority_score"] > result.iloc[1]["priority_score"]


def test_compute_score_invalid_weights():
    df = simple_dataset()
    invalid_weights = {
        "food_insecurity_rate_pct": 0.5,
        "distance_to_hub_km": 0.5,
        "stock_on_hand_tonnes": 0.5,
        "days_until_expiry": 0.5,
    }  # sum = 2.0, invalid
    with pytest.raises(ValueError, match="sum of the weights"):
        compute_score(df, weights=invalid_weights)


def test_generate_recommendation_contains_region_name():
    df = simple_dataset()
    result = compute_score(df)
    text = generate_recommendation(result.iloc[0])
    assert result.iloc[0]["region"] in text
