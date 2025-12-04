# There are over 79 columns a lot of which contains filler information
# I wanted to look at this from a business perspective so I recorded my insights and figured
# out what columns could be useful for this the rest of the columms,
# since they are not relevant have been dropped

import pandas as pd
import numpy as np
from src.utils.logging_utils import setup_logger

logger = setup_logger("clean_listings", "clean_listings.log")

# Filters out any unnecessary columns


def filter_columns(df):
    col_for_insights = [
        'id', 'property_type', 'room_type',
        'price', 'estimated_revenue_l365d',
        'accommodates', 'beds', 'bedrooms', 'bathrooms',
        'review_scores_rating', 'number_of_reviews', 'reviews_per_month',
        'availability_365', 'host_response_rate', 'host_response_time', 'host_since',
        'amenities', 'minimum_nights', 'maximum_nights',
        'latitude', 'longitude', 'neighbourhood_cleansed',
        'host_total_listings_count', 'host_is_superhost',
        'review_scores_cleanliness', 'review_scores_value', 'host_acceptance_rate'
    ]

    filtered_df = df[col_for_insights]

    return filtered_df

# Converts object dtype columns to string dtype


def convert_objects_to_string(df):
    obj_cols = df.select_dtypes(include="object").columns
    df[obj_cols] = df[obj_cols].astype("string")

    return df

# Converts price column to integer


def convert_price_to_int(df):
    if "price" in df.columns:
        df["price"] = pd.to_numeric(
            df["price"].astype("string")
            .str.replace(r"[^\d.]", "", regex=True),
            errors="coerce").astype("Int64")

    return df

# Converts beds and bedrooms into integer


def convert_bed_columns_to_int(df):
    for col in ["beds", "bedrooms"]:
        if col in df.columns:
            df[col] = (
                df[col].astype("string").replace("", np.nan)
                .astype("float").astype("Int64")
            )

    return df

# Converts host response & acceptance rate to integer from string percentage "97%"


def convert_rates_to_int(df):
    for col in ["host_response_rate", "host_acceptance_rate"]:
        if col in df.columns:
            df[col] = (
                df[col].astype("string")
                .str.replace("%", "", regex=False)
                .replace("", np.nan).astype("float").astype("Int64")
            )

    return df

# Converts host_since column into datetime


def convert_host_since(df):
    if "host_since" in df.columns:
        df["host_since"] = (
            pd.to_datetime(df["host_since"], errors="coerce")
            .dt.strftime("%Y-%m-%d")    # remove time component
        )
    return df

# Checks each indiividual value to see if it has t or f (or any other way of specifying)


def convert_superhost_to_bool(df):
    if "host_is_superhost" in df.columns:
        df["host_is_superhost"] = df["host_is_superhost"].apply(
            lambda x: True if str(x).strip().lower() in ["t", "true", "yes", "y"]
            else False if str(x).strip().lower() in ["f", "false", "no", "n"]
            else pd.NA
        ).astype("boolean")

    return df


OUTPUT_DIR = "data/processed"
FILE_NAME = "cleaned_listings.csv"

# Drop rows where host_is_superhost could not be determined.


def drop_missing_superhost(df):
    return df.dropna(subset=["host_is_superhost"])

# here we apply all the transformations in one go using a wrapper function.


def clean_listings(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()

    logger.info("Started Cleaning...")
    logger.info(f"Data Types (Before Cleaning): {clean_df.dtypes}\n")
    logger.info(f"Shape (Before Cleaning): {clean_df.shape}")

    clean_df = filter_columns(clean_df)
    clean_df = convert_objects_to_string(clean_df)
    clean_df = convert_price_to_int(clean_df)
    clean_df = convert_bed_columns_to_int(clean_df)
    clean_df = convert_rates_to_int(clean_df)
    clean_df = convert_host_since(clean_df)
    clean_df = convert_superhost_to_bool(clean_df)

    clean_df = drop_missing_superhost(clean_df)

    logger.info("Finished Cleaning.")
    logger.info(f"Data Types (After Cleaning): {clean_df.dtypes}")
    logger.info(f"Shape (After Cleaning): {clean_df.shape}\n")

    return clean_df
