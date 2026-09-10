"""
Interactive interface (Streamlit) for the food donation allocation tool.

Run with:
    streamlit run app.py

This interface contains NO new business logic: it only calls the
functions already written and tested in src/optimization.py and
src/scoring.py. This is good practice: separating the "engine" (tested,
reliable) from the "UI" (interface).
"""

import pandas as pd
import streamlit as st

from src.optimization import optimize_allocation

st.set_page_config(page_title="Food Donation Allocation", layout="wide")

st.title("Decision-Support Tool — Food Donation Allocation")
st.caption("Project built in preparation for the BCG Platinion Hackathon 2026 — Fighting World Hunger")

# ---------------------------------------------------------------
# Sidebar: parameters the user can adjust
# ---------------------------------------------------------------
st.sidebar.header("Parameters")

total_stock = st.sidebar.slider(
    "Total available stock (tonnes)",
    min_value=0, max_value=1000, value=300, step=10,
)

st.sidebar.subheader("Criteria weighting")
st.sidebar.caption("The sum must equal 100%.")

weight_insecurity = st.sidebar.slider("Food insecurity", 0, 100, 40, 5)
weight_expiry = st.sidebar.slider("Urgency (expiry)", 0, 100, 25, 5)
weight_stock = st.sidebar.slider("Stock already on hand", 0, 100, 20, 5)
weight_distance = st.sidebar.slider("Distance to hub", 0, 100, 15, 5)

weight_sum = weight_insecurity + weight_expiry + weight_stock + weight_distance

if weight_sum != 100:
    st.sidebar.error(f"The weights sum to {weight_sum}%, they must sum to 100%.")
    weights = None
else:
    weights = {
        "food_insecurity_rate_pct": weight_insecurity / 100,
        "days_until_expiry": weight_expiry / 100,
        "stock_on_hand_tonnes": weight_stock / 100,
        "distance_to_hub_km": weight_distance / 100,
    }

# ---------------------------------------------------------------
# Compute and display results
# ---------------------------------------------------------------
df = pd.read_csv("data/regions_real.csv")

if weights is not None:
    result, status = optimize_allocation(df, total_stock_tonnes=total_stock, weights=weights)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Allocation by region")
        st.bar_chart(result.set_index("region")["tonnes_allocated"])

    with col2:
        st.subheader("Summary")
        st.metric("Solver status", status)
        st.metric("Total allocated", f"{result['tonnes_allocated'].sum():.0f} t")
        served_regions = (result["tonnes_allocated"] > 0).sum()
        st.metric("Regions served", f"{served_regions} / {len(result)}")

    st.subheader("Detail by region")
    st.dataframe(
        result[[
            "region", "population", "food_insecurity_rate_pct",
            "priority_score", "max_capacity_tonnes", "tonnes_allocated",
        ]].rename(columns={
            "region": "Region",
            "population": "Population",
            "food_insecurity_rate_pct": "Food insecurity (%)",
            "priority_score": "Priority score",
            "max_capacity_tonnes": "Max capacity (t)",
            "tonnes_allocated": "Tonnes allocated",
        }),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Data sources"):
        st.markdown("""
        - **Population**: HCP, General Population and Housing Census
          (RGPH) 2024 — real data.
        - **Food insecurity rate**: proxy based on the HCP's
          multidimensional poverty rate (2024) — real for some regions,
          estimated for others (see `data/SOURCES.md`).
        - **Distance, stock, expiry**: fictional data (not publicly
          published, specific to each NGO's internal management).
        """)
