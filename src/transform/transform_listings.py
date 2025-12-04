
import pandas as pd
import numpy as np
from src.utils.logging_utils import setup_logger
import math


logger = setup_logger("transform_listings", "transform_listings.log")


# This drops rows where the percentage of missing values exceeds the given threshold.
# The default threshold is 0.40 means rows with more  than 40% missing values are removed.
def drop_rows_with_missing_threshold(df, threshold=0.40):

    # Calculates fraction of missing values per row
    missing_fraction = df.isna().mean(axis=1)

    # Identifies rows to drop
    rows_to_drop = missing_fraction[missing_fraction > threshold].index

    # Drops them
    df_cleaned = df.drop(index=rows_to_drop)

    return df_cleaned

# Cleans the amenities column by removing brackets/quotes and converting into a list of strings.


def clean_amenities_column(df):

    df["amenities"] = df["amenities"].apply(  # Applies a transformation to every value
        # If empty just return an empty list
        lambda value: [] if pd.isna(value)
        else [
            item.strip()  # Filters out any empty strings
            for item in (value.replace("[", "").replace("]", "")
                         .replace('"', "").replace("'", "")
                         # splits the strings into separate list items by the comma
                         ).split(",")
            if item.strip()
        ]
    )

    return df


def add_price_competitiveness(df):
    # Measures how competitively priced a listing is relative to its neighborhood & property type.

    group_median = df.groupby(
        ["neighbourhood_cleansed", "property_type"])["price"].median().rename("group_median_price")

    df = df.join(group_median, on=["neighbourhood_cleansed", "property_type"])

    # (price - median) / median price
    # If its below 0 it's underpriced and overpriced over 0
    df["price_competitiveness"] = (
        (df["price"] - df["group_median_price"]) / df["group_median_price"]
    )

    # Normalised to 0–100% scale for easier interpretation
    # The higher the more price competitive
    min_val = df["price_competitiveness"].min()
    max_val = df["price_competitiveness"].max()
    df["price_competitiveness"] = (
        (df["price_competitiveness"] - min_val) / (max_val - min_val)) * 100

    df["price_competitiveness"] = df["price_competitiveness"].round(2)

    df = df.rename(
        columns={"price_competitiveness": "price_competitiveness (100%)"})

    return df


def impute_price_column(df):
    # Flags rows where price or revenue was originally missing
    df["price"] = df["price"].astype(float)

    df["was_price_imputed"] = (
        df["price"].isna() | df["estimated_revenue_l365d"].isna()
    )

    # Impute price by neighbourhood + property_type median
    df["price"] = df.groupby(["neighbourhood_cleansed", "property_type"]
                             )["price"].transform(lambda x: x.fillna(x.median()))

    return df

# If a listing has 0 reviews, all review-related values should be 0.


def fix_review_columns(df):

    review_cols = [
        "review_scores_rating", "review_scores_cleanliness",
        "review_scores_value", "reviews_per_month"]

    unreviewed_prop = df["number_of_reviews"] == 0

    for col in review_cols:
        df.loc[unreviewed_prop, col] = 0

    return df

# Predicts how likely a listing is to be booked based on demand signals.


def add_occupancy_potential(df):
    # Calculates the occupancy score components
    availability_inv = 1 - (df["availability_365"] / 365)
    rev_norm = df["estimated_revenue_l365d"] / \
        df["estimated_revenue_l365d"].max()
    reviews_norm = df["reviews_per_month"] / df["reviews_per_month"].max()
    min_night_penalty = 1 / (df["minimum_nights"] + 1)

    # Weighted composite score
    score = (
        0.35 * availability_inv +
        0.30 * reviews_norm +
        0.25 * rev_norm +
        0.10 * min_night_penalty
    )

    # Normalize 0–1
    score = score / score.max()

    # Only add the final score column
    df["occupancy_potential"] = score.round(2)

    return df


def impute_minimum_beds(df):
    # Rename column once (safe if already renamed)
    if "beds" in df.columns:
        df = df.rename(columns={"beds": "minimum_beds"})

    # Flag: only rows where minimum_beds was missing
    df["was_beds_imputed"] = df["minimum_beds"].isna()

    # Fill missing minimum_beds using bedrooms
    df["minimum_beds"] = df.apply(
        lambda row: row["bedrooms"] if (pd.isna(row["minimum_beds"]) and not pd.isna(row["bedrooms"]))
        else row["minimum_beds"],
        axis=1
    )

    # Enforce logical rule: minimum_beds ≥ bedrooms
    df["minimum_beds"] = df[["minimum_beds", "bedrooms"]].max(axis=1)

    # to fix error
    df["minimum_beds"] = pd.to_numeric(
        df["minimum_beds"], errors="coerce").astype("Int64")

    return df


def impute_bathrooms(df):
    # Flag only missing bathroom values
    df["was_bathrooms_imputed"] = df["bathrooms"].isna()

    # Helper function
    def estimate_bathrooms(bedrooms):
        if pd.isna(bedrooms):
            return None
        if bedrooms <= 2:
            return 1
        if bedrooms == 3:
            return 2
        # general guideline: 2 bathrooms per 3 bedrooms
        return math.ceil((bedrooms / 3) * 2)

    df["bathrooms"] = df.apply(
        lambda row: estimate_bathrooms(row["bedrooms"])
        if pd.isna(row["bathrooms"])
        else row["bathrooms"],
        axis=1
    )

    return df


# Here we apply all the transformations in one go using a wrapper function.
def transform_listings(starting_df: pd.DataFrame) -> pd.DataFrame:
    df = starting_df.copy()

    logger.info("Started Transformations...")
    logger.info(f"Data Types (Before Transformations): {df.dtypes}")
    logger.info(f"Shape (Before Transformations): {df.shape}\n")

    # Most of these impute a lot of critical values
    df = impute_price_column(df)
    df = fix_review_columns(df)
    df = impute_minimum_beds(df)
    df = impute_bathrooms(df)

    # These drop rows with excessive missigness
    df = drop_rows_with_missing_threshold(df, threshold=0.22)

    # This cleans the amenities values
    df = clean_amenities_column(df)

    # Feature engineering
    df = add_price_competitiveness(df)
    df = add_occupancy_potential(df)

    df = df.reset_index(drop=True)

    logger.info("Finished Transformations")
    logger.info(f"Data Types (After Transformations): {df.dtypes}")
    logger.info(f"Shape (After Transformations): {df.shape}\n")

    return df
