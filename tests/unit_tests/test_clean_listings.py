import pandas as pd
from unittest.mock import patch
from src.transform.clean_listings import (
    filter_columns,
    convert_objects_to_string,
    convert_price_to_int,
    convert_bed_columns_to_int,
    convert_rates_to_int,
    convert_host_since,
    convert_superhost_to_bool,
    clean_listings,
)


class TestFilterColumns:
    def test_filter_columns_keeps_correct_columns(self):
        # I used the first row of the real dataset and added extra columns so I could check that the function removes everything it should
        df = pd.DataFrame({
            "id": [13913],
            "property_type": ["Private room in rental unit"],
            "room_type": ["Private room"],
            "price": [70.0],
            "estimated_revenue_l365d": [6440.0],
            "accommodates": [1],
            "beds": [1],
            "bedrooms": [1],
            "bathrooms": [1.0],
            "review_scores_rating": [4.85],
            "number_of_reviews": [55],
            "reviews_per_month": [0.3],
            "availability_365": [331],
            "host_response_rate": ["100%"],
            "host_response_time": ["within a few hours"],
            "host_since": ["2009-11-16"],
            "amenities": ["['Self check-in','Kitchen']"],
            "minimum_nights": [1],
            "maximum_nights": [29],
            "latitude": [51.56861],
            "longitude": [-0.1127],
            "neighbourhood_cleansed": ["Islington"],
            "host_total_listings_count": [5.0],
            "host_is_superhost": ["t"],
            "review_scores_cleanliness": [4.8],
            "review_scores_value": [4.78],
            "host_acceptance_rate": ["96%"],

            "waffle1": ["ABC"],
            "waffle2": [99],
            "waffle3": ["old mcdonald had a farm"]
        })

        result = filter_columns(df)

        expected_columns = [
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

        # I expect the function to only keep the useful columns and to still return one row
        assert list(result.columns) == expected_columns
        assert len(result) == 1


class TestConvertObjectsToString:
    def test_convert_objects_to_string_changes_dtype(self):
        df = pd.DataFrame({
            "col1": ["a", "b"],
            "col2": [1, 2]
        })

        result = convert_objects_to_string(df)
        assert result["col1"].dtype.name == "string"
        # I check here that other non object columns stay unchanged
        assert result["col2"].dtype != "string"


class TestConvertPriceToInt:
    def test_convert_price_to_int_parses_currency(self):
        df = pd.DataFrame({
            "price": ["$1,200", "$85.5", "300"]
        })

        result = convert_price_to_int(df)

        # I expect the function to clean the values and convert them into integers
        assert result["price"].tolist() == [1200, 85, 300]

    def test_convert_price_to_int_handles_invalid(self):
        df = pd.DataFrame({
            "price": ["abc", None]
        })

        result = convert_price_to_int(df)

        # I check that invalid or empty values become missing values
        assert pd.isna(result["price"][0])
        assert pd.isna(result["price"][1])


class TestConvertBedColumnsToInt:
    def test_convert_bed_columns_to_int_changes_dtypes(self):
        df = pd.DataFrame({
            "beds": ["2", "3"],
            "bedrooms": ["1", "4"]
        })

        result = convert_bed_columns_to_int(df)

        # I confirm that the new dtypes match the expected Int64 type
        assert str(result["beds"].dtype) == "Int64"
        assert str(result["bedrooms"].dtype) == "Int64"


class TestConvertRatesToInt:
    def test_convert_rates_to_int_removes_percent(self):
        df = pd.DataFrame({
            "host_response_rate": ["95%", "80%"],
            "host_acceptance_rate": ["100%", "50%"]
        })

        result = convert_rates_to_int(df)

        # I check that the percentages have been removed and converted into integers
        assert result["host_response_rate"].tolist() == [95, 80]
        assert result["host_acceptance_rate"].tolist() == [100, 50]


class TestConvertHostSince:
    def test_convert_host_since_parses_dates(self):
        df = pd.DataFrame({
            "host_since": ["2020-05-10", "invalid"]
        })

        result = convert_host_since(df)

        # I compare string versions of the values since the function returns strings
        assert str(result["host_since"][0]) == "2020-05-10"

        # Invalid values should convert into a missing date representation
        assert str(result["host_since"][1]) in ["NaT", "nan", "None"]


class TestConvertSuperhostToBool:
    def test_convert_superhost_to_bool_converts_values(self):
        df = pd.DataFrame({
            "host_is_superhost": ["t", "f", "yes", "no", "True", "False", "waffle"]
        })

        result = convert_superhost_to_bool(df)

        # I check all possible variations of true or false and ensure invalid values become NA
        assert result["host_is_superhost"].tolist() == [
            True, False, True, False, True, False, pd.NA
        ]


class TestCleanListings:
    @patch("src.transform.clean_listings.setup_logger")
    def test_clean_listings_pipeline(self, mock_logger):
        df = pd.DataFrame({
            "id": [1],
            "property_type": ["Apartment"],
            "room_type": ["Entire home"],
            "price": ["$150"],
            "estimated_revenue_l365d": [50000],
            "accommodates": [4],
            "beds": ["2"],
            "bedrooms": ["1"],
            "bathrooms": ["1"],
            "review_scores_rating": [4.85],
            "number_of_reviews": [120],
            "reviews_per_month": [1.2],
            "availability_365": [50],
            "host_response_rate": ["100%"],
            "host_response_time": ["within an hour"],
            "host_since": ["2018-02-01"],
            "amenities": ["[Wifi, TV]"],
            "minimum_nights": [2],
            "maximum_nights": [365],
            "latitude": [51.5],
            "longitude": [-0.1],
            "neighbourhood_cleansed": ["Camden"],
            "host_total_listings_count": [3],
            "host_is_superhost": ["t"],
            "review_scores_cleanliness": [4.9],
            "review_scores_value": [4.7],
            "host_acceptance_rate": ["95%"]
        })

        cleaned = clean_listings(df)

        # I check that numeric and boolean fields were converted correctly
        assert cleaned["price"].dtype == "Int64"
        assert cleaned["beds"].dtype == "Int64"
        assert cleaned["host_is_superhost"].dtype == "boolean"
        assert cleaned.shape[0] == 1

    @patch("src.transform.clean_listings.setup_logger")
    def test_clean_listings_keeps_required_columns(self, mock_logger):
        df = pd.DataFrame({
            "id": [1],
            "property_type": ["House"],
            "room_type": ["Private room"],
            "price": ["$100"],
            "estimated_revenue_l365d": [20000],
            "accommodates": [2],
            "beds": ["1"],
            "bedrooms": ["1"],
            "bathrooms": ["1"],
            "review_scores_rating": [4.5],
            "number_of_reviews": [30],
            "reviews_per_month": [0.5],
            "availability_365": [100],
            "host_response_rate": ["90%"],
            "host_response_time": ["within an hour"],
            "host_since": ["2020-01-01"],
            "amenities": ["[Wifi]"],
            "minimum_nights": [3],
            "maximum_nights": [30],
            "latitude": [51.6],
            "longitude": [-0.15],
            "neighbourhood_cleansed": ["Islington"],
            "host_total_listings_count": [1],
            "host_is_superhost": ["f"],
            "review_scores_cleanliness": [4.7],
            "review_scores_value": [4.6],
            "host_acceptance_rate": ["80%"]
        })

        cleaned = clean_listings(df)

        # I check that the number of expected columns stays consistent
        assert cleaned.shape[1] == 27
