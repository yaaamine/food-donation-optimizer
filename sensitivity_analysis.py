"""
Sensitivity analysis: how does the ranking change if we adjust the
weighting of the criteria?

This is meant to show that the model is understood, not just applied
blindly: we test 3 different strategies and observe the impact on the
top 3 priority regions.
"""

import pandas as pd

from src.scoring import compute_score

STRATEGIES = {
    "Balanced (default)": {
        "food_insecurity_rate_pct": 0.40,
        "days_until_expiry": 0.25,
        "stock_on_hand_tonnes": 0.20,
        "distance_to_hub_km": 0.15,
    },
    "Urgency-first (expiry)": {
        "food_insecurity_rate_pct": 0.25,
        "days_until_expiry": 0.45,
        "stock_on_hand_tonnes": 0.20,
        "distance_to_hub_km": 0.10,
    },
    "Logistics-first (ease of access)": {
        "food_insecurity_rate_pct": 0.25,
        "days_until_expiry": 0.15,
        "stock_on_hand_tonnes": 0.15,
        "distance_to_hub_km": 0.45,
    },
}


def main():
    df = pd.read_csv("data/regions.csv")

    print("=== SENSITIVITY ANALYSIS: impact of weighting on the TOP 3 ===\n")
    for strategy_name, weights in STRATEGIES.items():
        result = compute_score(df, weights=weights)
        top3 = ", ".join(result.head(3)["region"].tolist())
        print(f"[{strategy_name}]")
        print(f"  Top 3: {top3}\n")


if __name__ == "__main__":
    main()
