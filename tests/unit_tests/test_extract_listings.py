import os
import pytest
import pandas as pd
from pathlib import Path

from src.extract.extract_listings import (
    extract_listings,
    extract_listings_execution,
    TYPE,
    EXPECTED_IMPORT_RATE,
)


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("src.extract.extract_listings.logger")


@pytest.fixture
def mock_read_csv(mocker):
    return mocker.patch("src.extract.extract_listings.pd.read_csv")


def test_extract_listings_execution_loads_only_csv(mocker, tmp_path):
    # Create mock directory structure
    csv_file = tmp_path / "file1.csv"
    txt_file = tmp_path / "ignore.txt"
    csv_file.write_text("id,name\n1,Alice")
    txt_file.write_text("Not a CSV")

    # Mock raw folder path
    mocker.patch(
        "src.extract.extract_listings.Path.iterdir",
        return_value=[csv_file, txt_file],
    )

    mocker.patch(
        "src.extract.extract_listings.Path.exists", return_value=True
    )

    df_mock = pd.DataFrame({"id": [1], "name": ["Alice"]})
    mocker.patch("src.extract.extract_listings.pd.read_csv",
                 return_value=df_mock)

    result = extract_listings_execution()

    # Should only load the CSV file
    assert list(result.keys()) == ["file1"]
    assert isinstance(result["file1"], pd.DataFrame)


def test_extract_listings_returns_dict_of_dataframes(mocker, mock_logger):
    mock_df = pd.DataFrame({"id": [1]})

    mocker.patch(
        "src.extract.extract_listings.extract_listings_execution",
        return_value={"test_data": mock_df},
    )

    result = extract_listings()

    assert isinstance(result, dict)
    assert list(result.keys()) == ["test_data"]
    pd.testing.assert_frame_equal(result["test_data"], mock_df)

    # Logging should occur at least once
    mock_logger.info.assert_called()


def test_extract_listings_execution_raises_if_raw_folder_missing(mocker):
    mocker.patch(
        "src.extract.extract_listings.Path.exists",
        return_value=False
    )

    with pytest.raises(FileNotFoundError):
        extract_listings_execution()


def test_extract_listings_execution_raises_if_no_files(mocker):
    mocker.patch(
        "src.extract.extract_listings.Path.exists",
        return_value=True
    )

    mocker.patch(
        "src.extract.extract_listings.Path.iterdir",
        return_value=[]
    )

    with pytest.raises(FileNotFoundError):
        extract_listings_execution()


def test_extract_listings_execution_loads_multiple_csvs(mocker):
    csv1 = Path("/fake/file1.csv")
    csv2 = Path("/fake/file2.csv")

    # Simulate two CSV files
    mocker.patch(
        "src.extract.extract_listings.Path.iterdir",
        return_value=[csv1, csv2]
    )
    mocker.patch(
        "src.extract.extract_listings.Path.exists",
        return_value=True
    )

    df_mock = pd.DataFrame({"id": [1]})
    mocker.patch("src.extract.extract_listings.pd.read_csv",
                 return_value=df_mock)

    result = extract_listings_execution()

    assert set(result.keys()) == {"file1", "file2"}
    assert all(isinstance(df, pd.DataFrame) for df in result.values())


def test_extract_listings_logs_error_and_raises(mocker, mock_logger):
    mocker.patch(
        "src.extract.extract_listings.extract_listings_execution",
        side_effect=Exception("Boom!"),
    )

    with pytest.raises(Exception, match="Boom!"):
        extract_listings()

    mock_logger.error.assert_called_once()


def test_extract_listings_execution_read_csv_failure(mocker):
    csv_file = Path("/fake/file.csv")

    mocker.patch(
        "src.extract.extract_listings.Path.exists",
        return_value=True
    )
    mocker.patch(
        "src.extract.extract_listings.Path.iterdir",
        return_value=[csv_file]
    )

    mocker.patch(
        "src.extract.extract_listings.pd.read_csv",
        side_effect=Exception("Bad CSV"),
    )

    with pytest.raises(Exception):
        extract_listings_execution()
