"""
Core module: scoring and prioritization logic.

This module does NOT read/write any file and prints nothing: it only
contains the business logic, so it can be tested easily and reused
elsewhere (an API, a notebook, another script).
"""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = [
    "region",
    "population",
    "food_insecurity_rate_pct",
    "distance_to_hub_km",
    "stock_on_hand_tonnes",
    "days_until_expiry",
]

# Default weighting of the criteria (business choice, adjustable).
# The sum must always equal 1.0.
DEFAULT_WEIGHTS = {
    "food_insecurity_rate_pct": 0.40,  # 40%: the central criterion of the problem
    "days_until_expiry": 0.25,         # 25%: urgency, avoids waste
    "stock_on_hand_tonnes": 0.20,      # 20%: avoids over-supplying a region
    "distance_to_hub_km": 0.15,        # 15%: logistics factor, but secondary
                                        #      compared to the real need
}


def validate_data(df: pd.DataFrame) -> None:
    """Checks that the DataFrame has the expected columns and no missing
    or negative values. Raises an explicit ValueError otherwise."""
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in the data: {missing_columns}")

    if df[REQUIRED_COLUMNS[1:]].isnull().any().any():
        raise ValueError("The dataset contains missing values.")

    for col in REQUIRED_COLUMNS[1:]:
        if (df[col] < 0).any():
            raise ValueError(f"Column '{col}' contains negative values.")


def normalize(column: pd.Series) -> pd.Series:
    """Scales a column between 0 and 1 (min-max scaling).

    If all values are identical (min == max), returns a column of 0.5
    everywhere to avoid a division by zero.
    """
    value_range = column.max() - column.min()
    if value_range == 0:
        return pd.Series(0.5, index=column.index)
    return (column - column.min()) / value_range


def compute_score(df: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    """Computes the priority score of each region.

    Parameters
    ----------
    df : DataFrame containing at least the columns in REQUIRED_COLUMNS.
    weights : optional weighting dictionary; DEFAULT_WEIGHTS if not provided.
              Useful to test the ranking's sensitivity to the weighting.

    Returns
    -------
    DataFrame sorted by descending priority score, with the intermediate
    score columns and the final 'priority_score' column.
    """
    validate_data(df)
    weights = weights or DEFAULT_WEIGHTS

    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError(f"The sum of the weights must equal 1.0 (currently {sum(weights.values())}).")

    df = df.copy()

    df["insecurity_score"] = normalize(df["food_insecurity_rate_pct"])
    df["distance_score"] = 1 - normalize(df["distance_to_hub_km"])
    df["stock_score"] = 1 - normalize(df["stock_on_hand_tonnes"])
    df["expiry_score"] = 1 - normalize(df["days_until_expiry"])

    df["priority_score"] = (
        df["insecurity_score"] * weights["food_insecurity_rate_pct"]
        + df["distance_score"] * weights["distance_to_hub_km"]
        + df["stock_score"] * weights["stock_on_hand_tonnes"]
        + df["expiry_score"] * weights["days_until_expiry"]
    )

    return df.sort_values("priority_score", ascending=False).reset_index(drop=True)


def generate_recommendation(row: pd.Series) -> str:
    """Generates a short text explanation for a given region."""
    reasons = []
    if row["food_insecurity_rate_pct"] > 20:
        reasons.append("high food insecurity")
    if row["days_until_expiry"] <= 8:
        reasons.append("local stock close to expiry")
    if row["stock_on_hand_tonnes"] < 40:
        reasons.append("very limited stock on hand")
    if row["distance_to_hub_km"] < 150:
        reasons.append("fast delivery possible")

    if not reasons:
        reasons.append("less critical situation than other regions")

    return f"{row['region']}: priority because of " + ", ".join(reasons) + "."
