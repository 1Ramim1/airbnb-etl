import pandas as pd
import pytest
from unittest.mock import patch
from src.extract.extract import extract_data


"""
Component Tests for extract_data()

These tests validate extract_data() as an integration component that orchestrates
the extract_listings() function and handles all extracted datasets correctly.

Test Coverage:

1. Correct integration:
   - Ensures extract_data() correctly calls extract_listings()
   - Ensures the returned structure is a dictionary of DataFrames

2. Data integrity:
   - Ensures extracted data matches expected mock output

3. Error propagation:
   - Ensures exceptions from extract_listings() are propagated upward

4. Fail-fast behavior:
   - Ensures extract_data() does not hide errors

5. Logging behavior:
   - Ensures extract_data() emits at least one log (info-level)
"""


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def normalize_nulls(df):
    """Avoids None vs NaN mismatches during comparison."""
    return df.fillna(pd.NA).replace({pd.NA: None})


# ------------------------------------------------------------
# Test: extract_data returns correct structure & data
# ------------------------------------------------------------

@patch("src.extract.extract.extract_listings")
def test_extract_data_returns_correct_data(mock_extract_listings):
    """Verify extract_data correctly returns listing datasets."""
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
        normalize_nulls(result["listings"]),
        normalize_nulls(mock_df),
        check_dtype=False
    )


# ------------------------------------------------------------
# Test: extract_data propagates errors from extract_listings
# ------------------------------------------------------------

@patch("src.extract.extract.extract_listings")
def test_extract_data_propagates_exceptions(mock_extract_listings):
    """Ensure extract_data does not swallow errors from extract_listings."""
    mock_extract_listings.side_effect = Exception("Extraction failed")

    with pytest.raises(Exception, match="Extraction failed"):
        extract_data()


# ------------------------------------------------------------
# Test: extract_data logs extraction process
# ------------------------------------------------------------

@patch("src.extract.extract.logger")
@patch("src.extract.extract.extract_listings")
def test_extract_data_logs_actions(mock_extract_listings, mock_logger):
    """Ensure extract_data logs its steps."""
    mock_extract_listings.return_value = {
        "listings": pd.DataFrame({"id": [1]})
    }

    extract_data()

    # At least one info log must be emitted
    assert mock_logger.info.called


# ------------------------------------------------------------
# Test: extract_data returns multiple datasets if added later
# Future-proofing test
# ------------------------------------------------------------

@patch("src.extract.extract.extract_listings")
def test_extract_data_handles_multiple_datasets(mock_extract_listings):
    """Ensure extract_data supports multiple extracted datasets."""
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
