import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Price Competitiveness Insights",
                   layout="wide")

st.title("Price Competitiveness Insights")
st.write("""
This page is based on one of my own "feature engineering"/ my own metrics that I used to see how 
         competitively listings are priced relative to their **neighbourhood + property type** norms.

In terms of definition, 'Price Competitiveness' would be how far a listing is *above or below* the median price for similar listings.
         
- A higher score (toward 100%) would mean a listing is UNDERpriced and is cheaper relative to other listings (in their neighbourhood + property type)
         
- A higher score (toward 0%) would mean a listing is OVERpriced and is more expensive relative to other listings (in their neighbourhood + property type)
""")

df = st.session_state.df.copy()

# Rename for convenience
df["competitiveness"] = df["price_competitiveness (100%)"]

# Remove impossible values
df = df[df["competitiveness"].between(0, 100)]

# ----------------------------------------------------------
# Overall Distribution + Quartile Insight

st.subheader("Competitiveness Overview")

q1 = df["competitiveness"].quantile(0.25)
q2 = df["competitiveness"].quantile(0.50)
q3 = df["competitiveness"].quantile(0.75)

colA, colB, colC, colD = st.columns(4)
colA.metric("Median Competitiveness", f"{q2:.1f}%")
colB.metric("25th Percentile (Underpriced)", f"{q1:.1f}%")
colC.metric("75th Percentile (Overpriced)", f"{q3:.1f}%")
colD.metric("Most Overpriced Listing", f"{df['competitiveness'].max():.1f}%")

# Distribution plot
dist = (
    alt.Chart(df)
    .mark_area(opacity=0.7, color="#FF385C")
    .encode(
        x=alt.X("competitiveness:Q", bin=alt.Bin(
            maxbins=60), title="Competitiveness (%)"),
        y="count()"
    )
    .properties(height=250)
)
st.altair_chart(dist, use_container_width=True)

st.write("Most listings sit between 0–3%, potenitally showing limited price differentiation across similar listings.")

# ------------------------------------------------------------
# Relationship Between Competitiveness & Revenue

st.subheader("Does Being More Competitive Increase Revenue?")

scatter = (
    alt.Chart(df)
    .mark_circle(size=40, opacity=0.4, color="#23395B")
    .encode(
        x=alt.X("competitiveness:Q", title="Price Competitiveness (%)"),
        y=alt.Y("estimated_revenue_l365d:Q", title="Annual Revenue (£)"),
        tooltip=["price", "competitiveness", "estimated_revenue_l365d"]
    )
    .properties(height=300)
)

st.altair_chart(scatter, use_container_width=True)

corr = df["competitiveness"].corr(df["estimated_revenue_l365d"])
st.write(f"**Correlation between competitiveness and revenue:** `{corr:.3f}`")

#  It's overall a very weak correlation, however, it still shows a positive trend

st.success("Listings that are more competitively priced tend to earn *HIGHER revenue*. "
           "But only clearly to a certain extent. We can see that the graph shows us a weak positive correlation. ")


# ------------------------------------------------------------
# Competitiveness based on each Borough

st.subheader("Competitiveness based on each 'Neighbourhood' (Borough)")

neigh = (
    df.groupby("neighbourhood_cleansed")["competitiveness"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

bar = (
    alt.Chart(neigh.head(15))
    .mark_bar(color="#FF385C")
    .encode(
        x="competitiveness:Q",
        y=alt.Y("neighbourhood_cleansed:N", sort="-x"),
        tooltip=["neighbourhood_cleansed", "competitiveness"]
    )
    .properties(height=450)
)

st.altair_chart(bar, use_container_width=True)

st.write("""
Neighbourhoods at the top have *underpriced markets* on average, while those at the bottom 
tend to be **overpriced** relative to similar homes. Luckily, my own borough is placed quite high, meaning once I get enough capital, 
         I can invest in my neighbourhood. From this graph, we can clearly see only 2 boroughs stick out, Lambeth and Tower Hamlets. 
         The rest are quite closley clumped toegther.
""")

# ------------------------------------------------------------
# Competitiveness by Property Type

st.subheader("Property Type Comparison")

ptype = (
    df.groupby("property_type")["competitiveness"]
    .mean()
    .sort_values()
    .reset_index()
)

bar2 = (
    alt.Chart(ptype)
    .mark_bar(color="#23395B")
    .encode(
        x="competitiveness:Q",
        y=alt.Y("property_type:N", sort="-x"),
        tooltip=["property_type", "competitiveness"]
    )
    .properties(height=450)
)

st.altair_chart(bar2, use_container_width=True)

st.write("""
Some property types consistently price themselves more aggressively, revealing gaps in market understanding 
or differing demand patterns. We can see that here with hostels, nearly always being more competetively priced.
""")

# ------------------------------------------------------------
# Summary Insights

st.subheader("Summary Insights")

st.write("""
- Most listings cluster *very close* to neighbourhood medians. The actual competitiveness variance properties is small.  
- Neighbourhoods with **higher competitiveness scores** signal *undervalued opportunities*. Which is an interesting tool for an investor looking to buy a property.
- Competitiveness and revenue also show **weak correlation**, suggesting pricing alone does not drive performance.  
- From the last graph, we can also see that some property types systematically price themselves higher or lower than expected.  
""")
