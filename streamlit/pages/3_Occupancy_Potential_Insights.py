import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

st.set_page_config(page_title="Occupancy Potential Insights",
                   layout="wide")

st.title("Occupancy Potential Insights")
st.write("""
This page explores my second metric. The "Occupancy Potential" which is the predicted likelihood that a listing will get booked, based on:

- Availability  
- Monthly reviews  
- Revenue  
- Minimum night penalty  

Scores have a range from **0–1**, where higher values indicate **stronger booking potential**.
         
For example:
         'If two identical listings were put on the market, the one with a higher occupancy potential is more likely to attract more bookings.'
""")

df = st.session_state.df.copy()

col1, col2 = st.columns((2, 3))

# ------------------------------------------------------------
# General Stats

with col1:
    st.subheader("Summary Statistics")

    st.metric("Average Potential", f"{df['occupancy_potential'].mean():.2f}")
    st.metric("Highest Potential", f"{df['occupancy_potential'].max():.2f}")
    st.metric("Lowest Potential", f"{df['occupancy_potential'].min():.2f}")

# ------------------------------------------------------------
# Histogram

with col2:
    st.subheader("Distribution of Occupancy Potential")

    hist = (
        alt.Chart(df)
        .mark_bar(opacity=0.9, color="#FF385C")
        .encode(
            x=alt.X("occupancy_potential:Q", bin=alt.Bin(
                maxbins=40), title="Occupancy Potential"),
            y=alt.Y("count()", title="Count"),
            tooltip=["count()"]
        )
        .properties(height=300)
    )

    st.altair_chart(hist, use_container_width=True)

# ------------------------------------------------------------
# Neighbourhood Ranking

st.subheader("Average Occupancy Potential by 'Neighbourhood' (Borough)")

neigh = (
    df.groupby("neighbourhood_cleansed")["occupancy_potential"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

chart = (
    alt.Chart(neigh.head(20))
    .mark_bar(color="#23395B")
    .encode(
        x="occupancy_potential:Q",
        y=alt.Y("neighbourhood_cleansed:N", sort='-x'),
        tooltip=["neighbourhood_cleansed", "occupancy_potential"]
    )
    .properties(height=600)
)

st.altair_chart(chart, use_container_width=True)

# ------------------------------------------------------------
# Summary Insights

st.subheader("What This Means")

st.write("""
- A heavy concentration of listings are between 0.05 – 0.30. Fewer listings scoring above 0.60.
- Maximum scores near 1.0 are rare outliers.
- The ranking also shows that the top neighbourhoods have scores between 0.38 – 0.42. With Islington, Hackney, Lambeth and lambeth being top performers.
- Even though the differences are small (0.40 vs 0.35), they’re meaningful because the scale is compact.
""")
