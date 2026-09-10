"""
Decision-support tool for food donation allocation
====================================================

This script is the "V1" entry point: it answers the question "where
should we start?" with a simple weighted ranking, on a fictional dataset.

The scoring logic lives in src/scoring.py (separated, tested).
"""

import pandas as pd
import matplotlib.pyplot as plt

from src.scoring import compute_score, generate_recommendation


def main():
    df = pd.read_csv("data/regions.csv")
    df_scored = compute_score(df)

    print("\n=== REGION RANKING BY DONATION PRIORITY ===\n")
    for i, row in df_scored.iterrows():
        print(f"{i+1}. {row['region']:<28} score = {row['priority_score']:.2f}")

    print("\n=== RECOMMENDATIONS (TOP 5) ===\n")
    for _, row in df_scored.head(5).iterrows():
        print("- " + generate_recommendation(row))

    df_scored.to_csv("results/region_ranking.csv", index=False)

    plt.figure(figsize=(9, 6))
    plt.barh(df_scored["region"], df_scored["priority_score"], color="#1F3864")
    plt.xlabel("Priority score (0 to 1)")
    plt.title("Region prioritization for food donation allocation")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("results/region_ranking.png", dpi=150)

    print("\nChart saved to results/region_ranking.png")
    print("Full ranking saved to results/region_ranking.csv")


if __name__ == "__main__":
    main()
