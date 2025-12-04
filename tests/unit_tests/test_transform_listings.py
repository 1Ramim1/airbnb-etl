import pandas as pd
import numpy as np
from unittest.mock import patch

from src.transform.transform_listings import (
    drop_rows_with_missing_threshold,
    clean_amenities_column,
    add_price_competitiveness,
    impute_price_column,
    fix_review_columns,
    add_occupancy_potential,
    impute_minimum_beds,
    impute_bathrooms,
    transform_listings,
)


class TestDropRowsWithMissingThreshold:

    def test_drop_rows_with_missing_threshold_drops_high_missing_rows(self):
        df = pd.DataFrame({
            "a": [1, None, None],
            "b": [None, None, 3],
            "c": [1, None, None],
        })

        result = drop_rows_with_missing_threshold(df, threshold=0.5)

        # Only the first row has fewer than 50% missing
        assert len(result) == 1
        assert result.index.tolist() == [0]


class TestCleanAmenitiesColumn:

    def test_clean_amenities_column_parses_list_strings(self):
        df = pd.DataFrame({
            "amenities": ["['Wifi','TV','Kitchen']"]
        })

        result = clean_amenities_column(df)
        assert result["amenities"].iloc[0] == ["Wifi", "TV", "Kitchen"]

    def test_clean_amenities_handles_empty_values(self):
        df = pd.DataFrame({"amenities": [None]})
        result = clean_amenities_column(df)
        assert result["amenities"].iloc[0] == []


class TestAddPriceCompetitiveness:

    def test_price_competitiveness_computes_scaled_values(self):
        df = pd.DataFrame({
            "neighbourhood_cleansed": ["A", "A"],
            "property_type": ["House", "House"],
            "price": [100, 200],
        })

        result = add_price_competitiveness(df)

        # Column exists after rename
        assert "price_competitiveness (100%)" in result.columns

        # Values should be floats (scaled 0–100)
        vals = result["price_competitiveness (100%)"].tolist()
        assert all(isinstance(v, float) for v in vals)


class TestImputePriceColumn:

    def test_impute_price_column_fills_missing_prices(self):
        df = pd.DataFrame({
            "neighbourhood_cleansed": ["A", "A"],
            "property_type": ["House", "House"],
            "price": [100.0, None],
            "estimated_revenue_l365d": [5000, 4000]
        })

        result = impute_price_column(df)

        # Missing value filled with median = 100
        assert result["price"].tolist() == [100.0, 100.0]


class TestFixReviewColumns:

    def test_fix_review_columns_sets_review_data_to_zero_for_unreviewed(self):
        df = pd.DataFrame({
            "number_of_reviews": [0, 5],
            "review_scores_rating": [4.5, 4.0],
            "review_scores_cleanliness": [4.8, 4.5],
            "review_scores_value": [4.7, 4.5],
            "reviews_per_month": [1.2, 0.5],
        })

        result = fix_review_columns(df)

        assert result.loc[0, "review_scores_rating"] == 0
        assert result.loc[0, "reviews_per_month"] == 0
        assert result.loc[1, "review_scores_rating"] == 4.0


class TestAddOccupancyPotential:

    def test_add_occupancy_potential_adds_score(self):
        df = pd.DataFrame({
            "availability_365": [100, 200],
            "estimated_revenue_l365d": [10000, 20000],
            "reviews_per_month": [1, 2],
            "minimum_nights": [2, 3],
        })

        result = add_occupancy_potential(df)

        assert "occupancy_potential" in result.columns
        assert result["occupancy_potential"].dtype == float
        assert result["occupancy_potential"].max() <= 1.0  # normalized


class TestImputeMinimumBeds:

    def test_impute_minimum_beds_uses_bedrooms_when_missing(self):
        df = pd.DataFrame({
            "beds": [None, 2],
            "bedrooms": [1, 3]
        })

        result = impute_minimum_beds(df)

        assert result["minimum_beds"].tolist() == [1, 3]


class TestImputeBathrooms:

    def test_impute_bathrooms_applies_rules(self):
        df = pd.DataFrame({
            "bathrooms": [None, 2, None],
            "bedrooms": [1, 3, 4]
        })

        result = impute_bathrooms(df)

        # For bedrooms=1 → 1 bathroom
        # For bedrooms=4 → ceil((4/3)*2) = ceil(2.66) = 3
        assert result["bathrooms"].tolist() == [1, 2, 3]


class TestTransformListings:

    @patch("src.transform.transform_listings.setup_logger")  # Prevent file logs
    def test_transform_listings_full_pipeline(self, mock_logger):

        df = pd.DataFrame({
            "id": [1],
            "property_type": ["House"],
            "room_type": ["Entire home"],
            "price": [100.0],
            "estimated_revenue_l365d": [50000],
            "accommodates": [4],
            "beds": [2],
            "bedrooms": [2],
            "bathrooms": [1],
            "review_scores_rating": [4.8],
            "number_of_reviews": [10],
            "reviews_per_month": [0.5],
            "availability_365": [200],
            "host_response_rate": [95],
            "host_response_time": ["within an hour"],
            "host_since": ["2020-01-01"],
            "amenities": ["['Wifi','Kitchen']"],
            "minimum_nights": [2],
            "maximum_nights": [365],
            "latitude": [51.52],
            "longitude": [-0.1],
            "neighbourhood_cleansed": ["Camden"],
            "host_total_listings_count": [3],
            "host_is_superhost": [True],
            "review_scores_cleanliness": [4.7],
            "review_scores_value": [4.6],
            "host_acceptance_rate": [90]
        })

        result = transform_listings(df)

        # Pipeline should NOT drop the row
        assert len(result) == 1

        # Important engineered columns must be present
        assert "price_competitiveness (100%)" in result.columns
        assert "occupancy_potential" in result.columns
        assert "minimum_beds" in result.columns
        assert "was_price_imputed" in result.columns
        assert "was_bathrooms_imputed" in result.columns
