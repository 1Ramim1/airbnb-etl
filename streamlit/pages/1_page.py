import re
import csv
import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="London Airbnb Analysis", layout="wide")

# ---------------------------
# LOAD DATA
# ---------------------------


# @st.cache_data
# def load_data():
#     return pd.read_csv("data/raw/dirty_detailed_listings_data.csv")


# df = load_data()


INPUT_FILE = "data/raw/dirty_detailed_listings_data.csv"

print("🔧 Starting CSV Repair...")

# ------------------------------------------------------------
# STEP 1 — READ FILE AS RAW LINES (not as a DataFrame yet)
# ------------------------------------------------------------
with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    raw_lines = f.readlines()

print(f"Raw lines loaded: {len(raw_lines)}")

# ------------------------------------------------------------
# STEP 2 — Remove blank / whitespace-only lines
# ------------------------------------------------------------
clean_lines = [line for line in raw_lines if line.strip() != ""]
print(f"Lines after removing blanks: {len(clean_lines)}")

# ------------------------------------------------------------
# STEP 3 — Normalize delimiter issues
# Fix cases like:
#  - extra commas
#  - missing quotes
#  - malformed quoted strings
# ------------------------------------------------------------

normalized_lines = []
for line in clean_lines:
    # Replace repeated commas like ',,,,' with ','
    line = re.sub(r",\s*,+", ",", line)

    # Replace weird spaces around commas
    line = re.sub(r"\s+,", ",", line)

    # Normalize quotes
    line = line.replace('""', '"')

    normalized_lines.append(line)

print("Delimiter issues normalized.")

# ------------------------------------------------------------
# STEP 4 — Rewrite cleaned text to a temp file
# ------------------------------------------------------------
# TEMP_FILE = "data/raw/tmp_cleaned.csv"
with open(TEMP_FILE, "w", encoding="utf-8") as f:
    f.writelines(normalized_lines)

print("Temporary cleaned file written.")

# ------------------------------------------------------------
# STEP 5 — Try parsing with Pandas safely
# Set on_bad_lines='skip' to drop corrupted rows
# ------------------------------------------------------------
df = pd.read_csv(
    TEMP_FILE,
    low_memory=False,
    on_bad_lines="skip"  # skip rows with wrong column count
)

print(f"Rows parsed into DataFrame: {len(df)}")
print(f"Columns parsed: {len(df.columns)}")

# ------------------------------------------------------------
# STEP 6 — Remove columns that are completely empty
# ------------------------------------------------------------
df = df.dropna(axis=1, how='all')
print(f"Columns after removing empty ones: {len(df.columns)}")

# ------------------------------------------------------------
# STEP 7 — Fix numeric columns
# ------------------------------------------------------------
numeric_cols = [
    "price", "latitude", "longitude",
    "review_scores_rating", "review_scores_accuracy",
    "review_scores_cleanliness", "review_scores_checkin",
    "review_scores_communication", "review_scores_location",
    "review_scores_value",
    "calculated_host_listings_count",
    "calculated_host_listings_count_entire_homes",
    "calculated_host_listings_count_private_rooms",
    "calculated_host_listings_count_shared_rooms",
    "minimum_nights", "maximum_nights",
    "availability_30", "availability_60",
    "availability_90", "availability_365"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ------------------------------------------------------------
# STEP 8 — Fix date columns
# ------------------------------------------------------------
date_cols = ["last_scraped", "first_review", "last_review", "host_since"]

for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# ------------------------------------------------------------
# STEP 9 — Clean text-based columns
# ------------------------------------------------------------
if "neighbourhood_cleansed" in df.columns:
    df["neighbourhood_cleansed"] = (
        df["neighbourhood_cleansed"]
        .astype(str)
        .str.replace(r"[_\-]+", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

if "room_type" in df.columns:
    df["room_type"] = df["room_type"].astype(str).str.strip()

# ------------------------------------------------------------
# STEP 10 — Drop unusable rows
# ------------------------------------------------------------
df = df.dropna(subset=["latitude", "longitude", "price"])
print(f"Rows after dropping unusable entries: {len(df)}")

# ------------------------------------------------------------
# STEP 11 — Save final cleaned output
# ------------------------------------------------------------
# print(f"✅ CLEANED CSV SAVED → {OUTPUT_FILE}")


# ------------------------------------------------------------------------------------------------------------------------------------

# ---------------------------
# FIX PRICE COLUMN (IMPORTANT)
# ---------------------------
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df = df.dropna(subset=["price"])  # remove rows with invalid price

# ---------------------------
# TITLE
# ---------------------------
st.title("🏙️ London Airbnb Market Insights Dashboard")
st.write("Explore interactive insights generated from the cleaned Airbnb listings dataset.")

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("🔎 Filters")

neighbourhood = st.sidebar.multiselect(
    "Select Neighbourhood(s)",
    sorted(df["neighbourhood_cleansed"].dropna().unique())
)

room_type = st.sidebar.multiselect(
    "Select Room Type(s)",
    sorted(df["room_type"].dropna().unique())
)

# Slider now works because price is numeric
max_price = st.sidebar.slider(
    "Maximum Price (£)",
    float(df["price"].min()),
    float(df["price"].max()),
    float(df["price"].median())
)

# Apply filters
filtered_df = df.copy()

if neighbourhood:
    filtered_df = filtered_df[filtered_df["neighbourhood_cleansed"].isin(
        neighbourhood)]

if room_type:
    filtered_df = filtered_df[filtered_df["room_type"].isin(room_type)]

filtered_df = filtered_df[filtered_df["price"] <= max_price]

st.subheader("📊 Filter Summary")
st.write(f"Listings after filtering: **{len(filtered_df)}**")

# ---------------------------
# SECTION 1 — PRICE BY NEIGHBOURHOOD
# ---------------------------
st.header("💷 Price Analysis")

price_neighbourhood = (
    filtered_df.groupby("neighbourhood_cleansed")["price"]
    .mean()
    .reset_index()
    .sort_values("price", ascending=False)
)

fig_price = px.bar(
    price_neighbourhood,
    x="neighbourhood_cleansed",
    y="price",
    title="Average Price by Neighbourhood (Filtered)",
    labels={"price": "Average Price (£)",
            "neighbourhood_cleansed": "Neighbourhood"}
)
st.plotly_chart(fig_price, use_container_width=True)

# ---------------------------
# SECTION 2 — REVIEW SCORE HEATMAP
# ---------------------------
st.header("⭐ Review Score Correlations")

review_cols = [col for col in df.columns if "review_scores" in col]

if len(review_cols) > 1:
    corr = df[review_cols].corr()

    fig_corr = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="Viridis",
        title="Correlation Between Review Subscores"
    )
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.write("Not enough review score columns to generate correlation heatmap.")

# ---------------------------
# SECTION 3 — HOST BEHAVIOR
# ---------------------------
st.header("👤 Host Behaviour Insights")

fig_host = px.histogram(
    df,
    x="calculated_host_listings_count",
    nbins=50,
    title="Distribution of Host Listing Counts"
)
st.plotly_chart(fig_host, use_container_width=True)

# ---------------------------
# SECTION 4 — GEOGRAPHIC PRICE MAP
# ---------------------------
st.header("🗺️ Geographic Price Distribution")

if "latitude" in df.columns and "longitude" in df.columns:
    fig_map = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color="price",
        size="price",
        zoom=10,
        mapbox_style="carto-positron",
        title="Price Distribution Across London"
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.write("Latitude and longitude columns missing – cannot display map.")

# ---------------------------
# SECTION 5 — PRICE OUTLIERS
# ---------------------------
st.header("🚨 Price Outliers")

fig_box = px.box(
    df,
    y="price",
    title="Price Outliers Across All Listings"
)
st.plotly_chart(fig_box, use_container_width=True)
