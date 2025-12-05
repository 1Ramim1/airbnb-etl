# Imports
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json

from src.load.load import load_csv

# Page Setup
st.set_page_config(
    page_title="London Airbnb Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

# ------------------------------------
# CSS for the whole Dashboard
st.markdown(""" 
<style>
[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
}
[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* Airbnb-style metric cards */
[data-testid="stMetric"] {
    background-color: #ff385c !important;
    color: white !important;
    border-radius: 15px !important;
    padding: 20px 10px !important;
    text-align: center !important;
}
[data-testid="stMetricLabel"] > div {
    color: white !important;
    text-align: center !important;
}
[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 32px !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] {
    color: white !important;
}
[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    display: none !important;
}
            
[data-testid="stMetricLabel"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    text-align: center !important;
    color: white !important;
}
[data-testid="stMetricLabel"] > div {
    width: 100% !important;
    text-align: center !important;
    margin: 0 auto !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------
# Load Data
df = load_csv("data/processed/cleaned_listings.csv")

with open("data/output/neighbourhoods.geojson") as f:
    london_geo = json.load(f)

df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["neighbourhood"] = df["neighbourhood_cleansed"]

# ------------------------------------
# Here are the sidebar filters allowing us to look at different
# metrics across the different boroughs

with st.sidebar:
    st.title("London Airbnb Dashboard")

    room_types = df["room_type"].dropna().unique().tolist()
    selected_room = st.selectbox("Select Room Type", room_types)

    df_filtered = df[df["room_type"] == selected_room]

    metric_options = [
        "average_price",
        "count_listings",
        "estimated_revenue_l365d",
        "minimum_beds",
        "bedrooms",
        "bathrooms",
        "review_scores_rating",
        "host_is_superhost",
        "price_competitiveness (100%)",
        "occupancy_potential"
    ]
    selected_metric = st.selectbox("Metric for Map", metric_options)

# I tried to stay on theme with airbnbs colour theme
# after excessive colour palette research
CUSTOM_SCALE = ["#161925", "#23395B", "#FF385C"]

# ------------------------------------
# Here I grouped London into its "neighbourhoods" or "boroughs"
# This will ensure each borough is shaded according to its metrics
# Its called a chloropleth map
# I got the geojson location, which helped me etch out the corners of each
# borough

df_group = df_filtered.groupby("neighbourhood").agg(
    average_price=("price", "mean"),
    count_listings=("id", "count"),
    estimated_revenue_l365d=("estimated_revenue_l365d", "mean"),
    minimum_beds=("minimum_beds", "mean"),
    bedrooms=("bedrooms", "mean"),
    bathrooms=("bathrooms", "mean"),
    review_scores_rating=("review_scores_rating", "mean"),
    host_is_superhost=("host_is_superhost", "mean"),  # % superhosts
    price_competitiveness=("price_competitiveness (100%)", "mean"),
    occupancy_potential=("occupancy_potential", "mean")
).reset_index()

df_group = df_group.rename(
    columns={"price_competitiveness": "price_competitiveness (100%)"})


def make_choropleth(df_group, metric):
    fig = px.choropleth_mapbox(
        df_group,
        geojson=london_geo,
        locations="neighbourhood",
        featureidkey="properties.neighbourhood",
        color=metric,
        color_continuous_scale=CUSTOM_SCALE,
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat": 51.5072, "lon": -0.1276},
        opacity=0.6
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=350)
    return fig

# ------------------------------------
# I then used a barchart at the the bottom to show
# the top 10 across each metric, to be able to better visualise
# the scores across the map


def make_barchart(df_filtered):

    df_mean = (
        df_filtered.groupby("neighbourhood")["price"]
        .mean()
        .reset_index()
    )

    df_mean = df_mean.sort_values("price", ascending=False).head(10)

    BRAND_GRADIENT = ["#161925", "#A7BCDD", "#23395B", "#FF385C"]

    bar = (
        alt.Chart(df_mean)
        .mark_bar(size=25)
        .encode(
            x=alt.X("price:Q", title="Avg Price (£)"),
            y=alt.Y(
                "neighbourhood:N",
                sort=alt.SortField(field="price", order="descending"),
                title="Neighbourhood"
            ),
            color=alt.Color(
                "price:Q",
                scale=alt.Scale(range=BRAND_GRADIENT),
                legend=None
            ),
            tooltip=["neighbourhood", "price"]
        )
        .properties(width=900, height=450)
    )

    # When we hover over the graph, we'll be able to see labels with more
    # detail about the graph.

    text = (
        alt.Chart(df_mean)
        .mark_text(align="left", baseline="middle", dx=5, color="white")
        .encode(
            x="price:Q",
            y=alt.Y(
                "neighbourhood:N",
                sort=alt.SortField(field="price", order="descending")
            ),
            text=alt.Text("price:Q", format="£,.0f")
        )
    )

    return bar + text


# ------------------------------------
# On the left to fill the void,
# We used a Donut Chart to show the distribution of rooms
# I believe there is an error in this one

type_counts = (
    df.groupby("room_type")
    .size()
    .reset_index(name="listing_count")
)

donut = (
    alt.Chart(type_counts)
    .mark_arc(innerRadius=40)
    .encode(
        theta=alt.Theta("listing_count:Q", title="Listings"),
        color=alt.Color("room_type:N", title="Room Type"),
        tooltip=["room_type", "listing_count"]
    )
)

# ------------------------------------
# The dashboard is split into 2 rows to ensure the items are evenly aligned
# We start off with Key Metrics then Map then the Table
# This is the first row

row1_col1, row1_col2, row1_col3 = st.columns((1.5, 4.5, 2), gap="medium")

with row1_col1:
    st.markdown("#### Key Metrics")

    if not df_group.empty:
        max_price_row = df_group.loc[df_group["average_price"].idxmax()]
        st.metric(
            label=f"Most Expensive ({selected_room})",
            value=f"£{max_price_row['average_price']:.0f}",
            delta=max_price_row['neighbourhood']
        )

        max_list_row = df_group.loc[df_group["count_listings"].idxmax()]
        st.metric(
            label="Most Listings",
            value=int(max_list_row["count_listings"]),
            delta=max_list_row["neighbourhood"]
        )

        st.metric(
            label="Average Review Score",
            value=f"{df_filtered['review_scores_rating'].mean():.1f}"
        )

with row1_col2:
    st.markdown("#### Airbnb Map of London")
    fig = make_choropleth(df_group, selected_metric)
    st.plotly_chart(fig, use_container_width=True)

with row1_col3:
    st.markdown("#### Top Neighbourhoods")
    st.dataframe(
        df_group.sort_values(by=selected_metric, ascending=False).head(10),
        hide_index=True
    )

# ------------------------------------
# For row 2, it's broken down into a Donut, barchart and about the dashboard section

row2_col1, row2_col2, row2_col3 = st.columns((1.5, 4.5, 2), gap="medium")

with row2_col1:
    st.markdown("#### Room Type Distribution")
    st.altair_chart(donut, use_container_width=True)

with row2_col2:
    st.markdown("#### Top 10 Neighbourhoods (Avg Price)")
    st.altair_chart(make_barchart(df_filtered), use_container_width=True)

with row2_col3:
    st.markdown("#### About")
    with st.expander("About", expanded=True):
        st.write("""
        - Data Source: cleaned_listings.csv (that we cleaned!)  
        - Dynamic borough metrics  
        - Map uses official London neighbourhood boundaries (using GeoJson data I found online)
        - Top 10 barchart sorted by average price  
        """)
