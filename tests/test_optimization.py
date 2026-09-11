"""
Unit tests for the optimization module.
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.optimization import optimize_allocation


def simple_dataset() -> pd.DataFrame:
    """Three regions: one very high priority, one medium, one low priority.
    Max capacity ~= population * 0.00005."""
    return pd.DataFrame({
        "region": ["Critical_Region", "Medium_Region", "Comfortable_Region"],
        "population": [1_000_000, 1_000_000, 1_000_000],
        "food_insecurity_rate_pct": [30.0, 15.0, 5.0],
        "distance_to_hub_km": [500, 300, 50],
        "stock_on_hand_tonnes": [5, 50, 200],
        "days_until_expiry": [2, 15, 30],
    })


def test_optimal_solution_found():
    df = simple_dataset()
    result, status = optimize_allocation(df, total_stock_tonnes=30)
    assert status == "Optimal"


def test_does_not_exceed_total_stock():
    df = simple_dataset()
    total_stock = 30
    result, _ = optimize_allocation(df, total_stock_tonnes=total_stock)
    assert result["tonnes_allocated"].sum() <= total_stock + 1e-6


def test_does_not_exceed_max_capacity_per_region():
    df = simple_dataset()
    result, _ = optimize_allocation(df, total_stock_tonnes=1000)  # very large stock
    for _, row in result.iterrows():
        assert row["tonnes_allocated"] <= row["max_capacity_tonnes"] + 1e-6


def test_highest_priority_region_served_first():
    """With very scarce stock (well below all capacities, which are equal
    here since population is the same), all the stock should go to the
    highest-priority region."""
    df = simple_dataset()
    result, _ = optimize_allocation(df, total_stock_tonnes=10)  # scarce stock
    critical_row = result[result["region"] == "Critical_Region"].iloc[0]
    assert critical_row["tonnes_allocated"] == 10


def test_zero_stock_gives_no_allocation():
    df = simple_dataset()
    result, status = optimize_allocation(df, total_stock_tonnes=0)
    assert status == "Optimal"
    assert result["tonnes_allocated"].sum() == 0
