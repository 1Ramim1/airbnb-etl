import os
import timeit
from pathlib import Path
import pandas as pd

from src.utils.logging_utils import setup_logger

# Configure logger (same as reference)
logger = setup_logger(__name__, "extract_data.log")

TYPE = "LISTINGS from local file"
EXPECTED_IMPORT_RATE = 0.001


def extract_listings() -> pd.DataFrame:
    """
    Extract listings data from local data/raw directory,
    with performance logging (matches reference pattern).
    """
    try:
        start_time = timeit.default_timer()
        df = extract_listings_execution()
        extract_time = timeit.default_timer() - start_time

        logger.info(
            f"Extracted {df.shape[0]} rows in {extract_time:.2f}s ({TYPE})"
        )

        return df

    except Exception as e:
        logger.error(f"Failed to extract listings: {e}")
        raise


def extract_listings_execution() -> pd.DataFrame:
    """
    Actual extraction logic — no settings object required.
    Everything is built internally just like in the reference.
    """

    # Read filename from environment variables (reference-style)
    raw_filename = os.getenv("RAW_FILENAME", "input.csv")

    # Build raw folder path manually
    project_root = Path(__file__).resolve().parents[2]  # project root
    raw_dir = project_root / "data" / "raw"

    file_path = raw_dir / raw_filename

    if not file_path.exists():
        raise FileNotFoundError(f"Missing raw file: {file_path}")

    logger.info(f"Reading local raw file: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(file_path)
    elif suffix == ".json":
        df = pd.read_json(file_path)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    elif suffix == ".parquet":
        df = pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return df
