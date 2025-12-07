import pandas as pd
import pytest
from unittest.mock import patch
from src.extract.extract import extract_data


# I wrote these component tests so that extract_data() is checked as a full integration step.
# This function mainly coordinates extract_listings(), so I created these tests to confirm that behavior.
# I wanted to ensure the returned structure is correct, that data is preserved, and that errors are handled properly.


# I added this helper to make sure None and NaN do not cause false failures in comparisons.
def normalise_nulls(df):
    return df.fillna(pd.NA).replace({pd.NA: None})


# I wrote this test to confirm that extract_data returns the correct structure with the expected DataFrame content.
@patch("src.extract.extract.extract_listings")
def test_extract_data_returns_correct_data(mock_extract_listings):
    mock_df = pd.DataFrame({
        "id": [1, 2],
        "name": ["A", "B"]
    })
    mock_extract_listings.return_value = {"listings": mock_df}

    result = extract_data()

    assert isinstance(result, dict)
    assert "listings" in result
    assert isinstance(result["listings"], pd.DataFrame)

    pd.testing.assert_frame_equal(
        normalise_nulls(result["listings"]),
        normalise_nulls(mock_df),
        check_dtype=False
    )


# I wrote this test so that any exception raised inside extract_listings is passed upward unchanged.
@patch("src.extract.extract.extract_listings")
def test_extract_data_propagates_exceptions(mock_extract_listings):
    mock_extract_listings.side_effect = Exception("Extraction failed")

    with pytest.raises(Exception, match="Extraction failed"):
        extract_data()


# I added this test to confirm that extract_data writes log messages while running.
@patch("src.extract.extract.logger")
@patch("src.extract.extract.extract_listings")
def test_extract_data_logs_actions(mock_extract_listings, mock_logger):
    mock_extract_listings.return_value = {
        "listings": pd.DataFrame({"id": [1]})
    }

    extract_data()

    # I check that at least one info log was recorded
    assert mock_logger.info.called


# I included this test so that extract_data will continue working correctly even if more datasets are added in the future.
@patch("src.extract.extract.extract_listings")
def test_extract_data_handles_multiple_datasets(mock_extract_listings):
    mock_extract_listings.return_value = {
        "detailed_listings_data": pd.DataFrame({"id": [1]}),
        "review_data": pd.DataFrame({"review": ["Excellent"]})
    }

    result = extract_data()

    assert set(result.keys()) == {
        "detailed_listings_data",
        "review_data",
    }

    assert isinstance(result["review_data"], pd.DataFrame)
