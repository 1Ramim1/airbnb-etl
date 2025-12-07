import pandas as pd
import ast
import pytest
from unittest.mock import patch
from src.transform.transform_data import transform_data


# I added this helper so I can avoid failing tests due to differences between None and NA.
def normalise(df):
    df = df.copy().reset_index(drop=True)
    return df.replace({None: pd.NA})


# I load the real raw listings file here so that the test uses actual source data.
@pytest.fixture
def sample_listings():
    df = pd.read_csv("data/raw/detailed_listings_data.csv")
    return normalise(df)


# I load the expected cleaned listings and convert the amenities column back into lists
# because this helps compare the real output to the expected output accurately.
@pytest.fixture
def expected_transformed_listings():
    df = pd.read_csv("tests/test_data/expected_cleaned_listings.csv")

    if "amenities" in df.columns:
        df["amenities"] = df["amenities"].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )

    return df


# I wrote this test so that I can confirm the full transformation pipeline works properly from start to finish.
def test_transform_data_returns_correct_output(
    sample_listings, expected_transformed_listings
):
    result = transform_data(sample_listings)

    pd.testing.assert_frame_equal(
        normalise(result),
        normalise(expected_transformed_listings),
        check_dtype=False,
    )


# I added this test so that failures inside clean_listings are passed up correctly.
@patch("src.transform.transform_data.clean_listings")
def test_transform_data_propagates_clean_listings_exception(
    mock_clean_listings,
):
    mock_clean_listings.side_effect = Exception("Cleaning failed")

    with pytest.raises(Exception, match="Cleaning failed"):
        transform_data(pd.DataFrame())


# I created this test to make sure that errors in transform_listings are not hidden.
@patch("src.transform.transform_data.transform_listings")
@patch("src.transform.transform_data.clean_listings")
def test_transform_data_propagates_transform_listings_exception(
    mock_clean_listings, mock_transform_listings
):
    mock_clean_listings.return_value = pd.DataFrame({"id": [1]})
    mock_transform_listings.side_effect = Exception("Transform failed")

    with pytest.raises(Exception, match="Transform failed"):
        transform_data(pd.DataFrame())


# I wrote this test so that the function stops immediately if clean_listings fails.
@patch("src.transform.transform_data.transform_listings")
@patch("src.transform.transform_data.clean_listings")
def test_transform_data_fails_fast_does_not_continue(
    mock_clean_listings, mock_transform_listings
):
    mock_clean_listings.side_effect = Exception("Clean error")

    with pytest.raises(Exception, match="Clean error"):
        transform_data(pd.DataFrame())

    # I check that transform_listings was not called since the first step already failed
    mock_transform_listings.assert_not_called()


# I added this test to make sure the final dataset is saved when everything succeeds.
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
