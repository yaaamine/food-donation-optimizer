"""
Optimization module: allocating a limited donation stock across regions.
============================================================================

Difference from the first script (prioritize_donations.py):
    - prioritize_donations.py answers "where should we start?" (a ranking)
    - this module answers "how much should we send to each region?" given
      a limited total stock and capacity constraints

This is a LINEAR PROGRAMMING problem: we look for the values of
x_1, x_2, ..., x_12 (tonnes allocated to each region) that MAXIMIZE an
objective function, subject to a set of linear CONSTRAINTS.

We use the PuLP library, which lets us write the problem almost as we
would on paper, then solve it with a solver (CBC, bundled with PuLP by
default).
"""

from __future__ import annotations

import pandas as pd
import pulp

from src.scoring import compute_score, validate_data


def build_max_capacity(df_score: pd.DataFrame, tonnes_per_capita: float = 0.00005) -> pd.Series:
    """Defines a maximum absorption capacity per region.

    Simplifying assumption, explicitly stated: a region cannot absorb
    more than a quantity proportional to its population (beyond that,
    the surplus would be useless or impossible to distribute in time).

    Parameters
    ----------
    df_score : DataFrame containing at least the 'region' and 'population' columns
    tonnes_per_capita : scaling factor (tonnes per inhabitant), to be
        adjusted according to the real context (e.g. how many people a
        tonne of food can cover over a given period)
    """
    return df_score["population"] * tonnes_per_capita


def optimize_allocation(df: pd.DataFrame, total_stock_tonnes: float, weights: dict | None = None) -> tuple[pd.DataFrame, str]:
    """Solves the optimal allocation problem for a limited stock.

    Returns the original DataFrame enriched with a 'tonnes_allocated' and
    'max_capacity_tonnes' column, sorted by descending allocated tonnes,
    along with the solver status.
    """
    validate_data(df)

    # 1. Reuse the already-built and tested scoring (src/scoring.py) to
    #    get a priority score per region.
    df_score = compute_score(df, weights=weights)

    # 2. Define a maximum absorption capacity per region.
    df_score["max_capacity_tonnes"] = build_max_capacity(df_score)

    # 3. Declare the optimization problem: we want to MAXIMIZE the objective.
    problem = pulp.LpProblem("Food_donation_allocation", pulp.LpMaximize)

    # 4. Decision variables: a continuous quantity (>= 0) per region.
    variables = {
        region: pulp.LpVariable(f"tonnes_{i}", lowBound=0)
        for i, region in enumerate(df_score["region"])
    }

    # 5. Objective function: maximize the sum (priority_score * tonnes allocated).
    #    The more a region is a priority, the more each tonne allocated to
    #    it "pays off" in the objective -> the algorithm is incentivized to
    #    fill the most priority regions first.
    problem += pulp.lpSum(
        row["priority_score"] * variables[row["region"]]
        for _, row in df_score.iterrows()
    )

    # 6. Constraint 1: total allocated must not exceed the available stock.
    problem += pulp.lpSum(variables.values()) <= total_stock_tonnes, "Total_stock_available"

    # 7. Constraint 2: each region cannot receive more than its max capacity.
    for _, row in df_score.iterrows():
        problem += variables[row["region"]] <= row["max_capacity_tonnes"], f"Max_capacity_{row['region']}"

    # 8. Solve the problem (the CBC solver, bundled with PuLP, does the work).
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    # 9. Retrieve the results into the DataFrame.
    df_score["tonnes_allocated"] = df_score["region"].map(lambda r: variables[r].value())
    df_score = df_score.sort_values("tonnes_allocated", ascending=False).reset_index(drop=True)

    return df_score, pulp.LpStatus[problem.status]
