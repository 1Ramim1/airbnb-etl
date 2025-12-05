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

# I wrote these component tests so that extract_listings() is validated as a real working unit.
# These tests load the actual CSV files, use the real filesystem, and confirm that everything works end to end.
# I preferred not to mock pandas here because I want to confirm that the data loads exactly as expected.


# I load every CSV inside data/raw so that I can compare the function output to real known data.
@pytest.fixture
def expected_raw_data():
    raw_dir = Path("data/raw")
    csv_files = list(raw_dir.glob("*.csv"))

    expected = {}
    for fp in csv_files:
        expected[fp.stem] = pd.read_csv(fp)

    return expected


# This test checks that extract_listings actually loads every real CSV into a dataframe correctly.
def test_extract_listings_returns_correct_data(expected_raw_data):
    result = extract_listings()

    assert isinstance(result, dict)
    assert set(result.keys()) == set(expected_raw_data.keys())

    # I compare each dataframe to make sure the content matches exactly.
    for name, df in expected_raw_data.items():
        pd.testing.assert_frame_equal(result[name], df)


# I wrote this performance test to measure rows per second because this scales better for large datasets.
def test_extract_listings_performance(expected_raw_data):

    execution_time = timeit.timeit(
        "extract_listings()",
        globals=globals(),
        number=1,
    )

    total_rows = sum(df.shape[0] for df in expected_raw_data.values())
    assert total_rows > 0

    rows_per_second = total_rows / execution_time

    # I set a reasonable threshold based on what a local machine should handle.
    minimum_expected_rps = 40_000

    assert rows_per_second >= minimum_expected_rps, (
        f"Expected >= {minimum_expected_rps} rows/sec, "
        f"but got {rows_per_second:.2f} rows/sec"
    )


# I wrote this test to ensure a missing raw folder raises a clear and meaningful error.
@patch("src.extract.extract_listings.Path.exists", return_value=False)
def test_extract_listings_raises_if_raw_folder_missing(mock_exists):
    with pytest.raises(FileNotFoundError, match="Raw folder not found"):
        extract_listings_execution()


# This test checks that the function handles an empty directory by raising an appropriate error.
@patch("src.extract.extract_listings.Path.exists", return_value=True)
@patch("src.extract.extract_listings.Path.iterdir", return_value=[])
def test_extract_listings_raises_if_no_files(mock_iterdir, mock_exists):
    with pytest.raises(FileNotFoundError, match="No files found"):
        extract_listings_execution()


# I created this test to simulate a corrupt CSV file and confirm that the function does not fail silently.
def test_extract_listings_corrupt_file(tmp_path):
    corrupt_dir = tmp_path / "raw"
    corrupt_dir.mkdir()

    corrupt_file = corrupt_dir / "corrupt.csv"
    # minimal content should cause pandas to error
    corrupt_file.write_text(",,,,,,")

    # I patch the paths so that extract_listings reads from my temporary corrupt folder.
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
