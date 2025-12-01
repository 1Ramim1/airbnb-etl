import os
import pandas as pd
import pytest
from pathlib import Path

from src.extract.extract_listings import extract_listings_execution, extract_listings
from src.extract.extract import extract_data


# ---------------------------------------------------------------------
# Test 1 — data/raw folder exists in real project
# ---------------------------------------------------------------------
def test_raw_folder_exists():
    project_root = Path(__file__).resolve(
    ).parents[1].parents[0]  # tests/ → project root
    raw_dir = project_root / "data" / "raw"

    assert raw_dir.exists(), "data/raw folder does not exist"
    assert raw_dir.is_dir(), "data/raw is not a directory"


# ---------------------------------------------------------------------
# Test 2 — data/raw contains at least one file
# ---------------------------------------------------------------------
def test_raw_folder_contains_files():
    project_root = Path(__file__).resolve().parents[1].parents[0]
    raw_dir = project_root / "data" / "raw"

    files = list(raw_dir.iterdir())
    assert len(files) > 0, "data/raw folder is empty — add a test file"


# ---------------------------------------------------------------------
# Helper to get a real existing file from data/raw
# ---------------------------------------------------------------------
def get_any_raw_file():
    project_root = Path(__file__).resolve().parents[1].parents[0]
    raw_dir = project_root / "data" / "raw"
    for f in raw_dir.iterdir():
        if f.is_file():
            return f
    raise FileNotFoundError("No files found in data/raw")


# ---------------------------------------------------------------------
# Test 3 — extract_listings_execution can read the file
# ---------------------------------------------------------------------
def test_extract_listings_execution():
    file_path = get_any_raw_file()

    # Use filename from your real folder
    os.environ["RAW_FILENAME"] = file_path.name

    df = extract_listings_execution()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0, "Extracted dataframe is empty"


# ---------------------------------------------------------------------
# Test 4 — extract_listings wrapper works
# ---------------------------------------------------------------------
def test_extract_listings_wrapper():
    file_path = get_any_raw_file()

    os.environ["RAW_FILENAME"] = file_path.name

    df = extract_listings()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


# ---------------------------------------------------------------------
# Test 5 — extract_data orchestrator works
# ---------------------------------------------------------------------
def test_extract_data():
    file_path = get_any_raw_file()

    os.environ["RAW_FILENAME"] = file_path.name

    df = extract_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
