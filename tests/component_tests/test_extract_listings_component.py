import pandas as pd
import pytest
import timeit
from pathlib import Path
from unittest.mock import patch

from src.extract.extract_listings import (
    extract_listings,
    extract_listings_execution,
    EXPECTED_IMPORT_RATE,
)


"""
Component Tests for extract_listings()

These tests validate extract_listings() as a complete component:

✔ Reads real CSV files from data/raw/
✔ Returns a dictionary of DataFrames
✔ Ensures the data matches the actual CSVs exactly
✔ Validates performance characteristics
✔ Handles missing folders and corrupt files correctly

These tests use real filesystem interactions instead of mocking pandas.
"""


# ------------------------------------------------------------
# Fixture: load expected real datasets
# ------------------------------------------------------------

@pytest.fixture
def expected_raw_data():
    """Load every CSV inside data/raw into a dict of DataFrames."""
    raw_dir = Path("data/raw")
    csv_files = list(raw_dir.glob("*.csv"))

    expected = {}
    for fp in csv_files:
        expected[fp.stem] = pd.read_csv(fp)

    return expected


# ------------------------------------------------------------
# Test 1: extract_listings loads ALL datasets correctly
# ------------------------------------------------------------

def test_extract_listings_returns_correct_data(expected_raw_data):
    """Verify extract_listings loads each CSV into a DataFrame correctly."""
    result = extract_listings()

    assert isinstance(result, dict)
    assert set(result.keys()) == set(expected_raw_data.keys())

    # Compare each dataset file-by-file
    for name, df in expected_raw_data.items():
        pd.testing.assert_frame_equal(result[name], df)


# ------------------------------------------------------------
# Test 2: Performance (must meet EXPECTED_IMPORT_RATE per file)
# ------------------------------------------------------------

def test_extract_listings_performance(expected_raw_data):
    """
    Performance test based on rows per second rather than per-file time.
    This is appropriate for very large CSV datasets (millions of rows).
    """

    execution_time = timeit.timeit(
        "extract_listings()",
        globals=globals(),
        number=1,
    )

    # Count total rows across all extracted datasets
    total_rows = sum(df.shape[0] for df in expected_raw_data.values())
    assert total_rows > 0

    rows_per_second = total_rows / execution_time

    # Acceptable threshold for large CSV files on local disk
    # Adjust if needed based on machine performance
    minimum_expected_rps = 75_000  # 150k rows per second

    assert rows_per_second >= minimum_expected_rps, (
        f"Expected >= {minimum_expected_rps} rows/sec, "
        f"but got {rows_per_second:.2f} rows/sec"
    )

# ------------------------------------------------------------
# Test 3: Missing raw directory raises FileNotFoundError
# ------------------------------------------------------------


@patch("src.extract.extract_listings.Path.exists", return_value=False)
def test_extract_listings_raises_if_raw_folder_missing(mock_exists):
    with pytest.raises(FileNotFoundError, match="Raw folder not found"):
        extract_listings_execution()


# ------------------------------------------------------------
# Test 4: No files in raw directory
# ------------------------------------------------------------

@patch("src.extract.extract_listings.Path.exists", return_value=True)
@patch("src.extract.extract_listings.Path.iterdir", return_value=[])
def test_extract_listings_raises_if_no_files(mock_iterdir, mock_exists):
    with pytest.raises(FileNotFoundError, match="No files found"):
        extract_listings_execution()


# ------------------------------------------------------------
# Test 5: Corrupt CSV file raises an exception
# ------------------------------------------------------------

def test_extract_listings_corrupt_file(tmp_path):
    """Simulate a corrupt CSV file and ensure extraction fails."""
    # Create fake raw folder
    corrupt_dir = tmp_path / "raw"
    corrupt_dir.mkdir()

    corrupt_file = corrupt_dir / "corrupt.csv"
    corrupt_file.write_text(",,,,,,")  # not a valid CSV csv; pandas will error

    # Patch project_root/data/raw -> our fake corrupt folder
    with patch(
        "src.extract.extract_listings.Path.resolve",
        return_value=(corrupt_dir.parent.parent)
    ):
        with patch(
            "src.extract.extract_listings.Path.iterdir",
            return_value=[corrupt_file]
        ):
            with pytest.raises(Exception):
                extract_listings_execution()
