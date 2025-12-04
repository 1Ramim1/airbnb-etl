import pandas as pd
import ast
import pytest
from unittest.mock import patch
from src.transform.transform_data import transform_data


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def normalize(df):
    df = df.copy().reset_index(drop=True)

    # Only normalize NaN vs <NA> differences
    return df.replace({None: pd.NA})

# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------


@pytest.fixture
def sample_listings():
    """Load a real raw Airbnb listings CSV file."""
    df = pd.read_csv("data/raw/detailed_listings_data.csv")
    return normalize(df)


@pytest.fixture
def expected_transformed_listings():
    df = pd.read_csv("tests/test_data/expected_cleaned_listings.csv")

    if "amenities" in df.columns:
        df["amenities"] = df["amenities"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )

    return df

# def expected_transformed_listings():
#     """Expected result of clean_listings + transform_listings."""
#     return pd.read_csv("tests/test_data/expected_cleaned_listings.csv")

# ---------------------------------------------------------
# Test 1 — FULL PIPELINE WORKS END-TO-END
# ---------------------------------------------------------


def test_transform_data_returns_correct_output(
    sample_listings, expected_transformed_listings
):
    result = transform_data(sample_listings)

    pd.testing.assert_frame_equal(
        normalize(result),
        normalize(expected_transformed_listings),
        check_dtype=False,
    )


# ---------------------------------------------------------
# Test 2 — ERROR PROPAGATION: clean_listings
# ---------------------------------------------------------

@patch("src.transform.transform_data.clean_listings")
def test_transform_data_propagates_clean_listings_exception(
    mock_clean_listings,
):
    mock_clean_listings.side_effect = Exception("Cleaning failed")

    with pytest.raises(Exception, match="Cleaning failed"):
        transform_data(pd.DataFrame())


# ---------------------------------------------------------
# Test 3 — ERROR PROPAGATION: transform_listings
# ---------------------------------------------------------

@patch("src.transform.transform_data.transform_listings")
@patch("src.transform.transform_data.clean_listings")
def test_transform_data_propagates_transform_listings_exception(
    mock_clean_listings, mock_transform_listings
):
    mock_clean_listings.return_value = pd.DataFrame({"id": [1]})
    mock_transform_listings.side_effect = Exception("Transform failed")

    with pytest.raises(Exception, match="Transform failed"):
        transform_data(pd.DataFrame())


# ---------------------------------------------------------
# Test 4 — FAIL-FAST: clean_listings fails → transform_listings NOT called
# ---------------------------------------------------------

@patch("src.transform.transform_data.transform_listings")
@patch("src.transform.transform_data.clean_listings")
def test_transform_data_fails_fast_does_not_continue(
    mock_clean_listings, mock_transform_listings
):
    mock_clean_listings.side_effect = Exception("Clean error")

    with pytest.raises(Exception, match="Clean error"):
        transform_data(pd.DataFrame())

    # Must NOT execute transform_listings
    mock_transform_listings.assert_not_called()


# ---------------------------------------------------------
# Test 5 — save_dataframe_to_csv is called
# ---------------------------------------------------------

@patch("src.transform.transform_data.save_dataframe_to_csv")
@patch("src.transform.transform_data.transform_listings")
@patch("src.transform.transform_data.clean_listings")
def test_transform_data_saves_output(
    mock_clean_listings,
    mock_transform_listings,
    mock_save,
):
    mock_clean_listings.return_value = pd.DataFrame({"id": [1]})
    mock_transform_listings.return_value = pd.DataFrame({"id": [1]})

    transform_data(pd.DataFrame())

    mock_save.assert_called_once()
