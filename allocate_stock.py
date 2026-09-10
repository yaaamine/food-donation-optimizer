"""
Entry point: optimal allocation of a food donation stock across Morocco's
12 regions, using real demographic and poverty data (see data/SOURCES.md
for the detail of the sources).

Usage:
    python allocate_stock.py --stock 300
"""

import argparse

import pandas as pd
import matplotlib.pyplot as plt

from src.optimization import optimize_allocation


def main():
    parser = argparse.ArgumentParser(description="Optimal allocation of a food donation stock.")
    parser.add_argument("--stock", type=float, default=300, help="Total available stock, in tonnes.")
    parser.add_argument("--data", type=str, default="data/regions_real.csv", help="Path to the data file.")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    result, status = optimize_allocation(df, total_stock_tonnes=args.stock)

    print(f"\nSolver status: {status}")
    print(f"Total stock to distribute: {args.stock} tonnes\n")
    print("=== OPTIMAL ALLOCATION BY REGION ===\n")
    for _, row in result.iterrows():
        if row["tonnes_allocated"] > 0:
            print(f"{row['region']:<28} {row['tonnes_allocated']:>7.1f} t  "
                  f"(priority score = {row['priority_score']:.2f}, "
                  f"max capacity = {row['max_capacity_tonnes']:.1f} t)")

    unserved = result[result["tonnes_allocated"] == 0]
    if not unserved.empty:
        print(f"\n{len(unserved)} region(s) not served due to insufficient stock: "
              f"{', '.join(unserved['region'].tolist())}")

    result.to_csv("results/optimal_allocation.csv", index=False)

    plt.figure(figsize=(9, 6))
    colors = ["#1F3864" if t > 0 else "#CCCCCC" for t in result["tonnes_allocated"]]
    plt.barh(result["region"], result["tonnes_allocated"], color=colors)
    plt.xlabel("Tonnes allocated")
    plt.title(f"Optimal allocation of a {args.stock:.0f}-tonne stock")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("results/optimal_allocation.png", dpi=150)

    print("\nResults saved to results/optimal_allocation.csv and .png")


if __name__ == "__main__":
    main()
