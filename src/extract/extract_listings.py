import os
import timeit
from pathlib import Path
import pandas as pd

from src.utils.logging_utils import setup_logger

# Configure logger (same as reference)
logger = setup_logger(__name__, "extract_data.log")

TYPE = "LISTINGS from local file"
EXPECTED_IMPORT_RATE = 0.001


def extract_listings() -> dict[str, pd.DataFrame]:
    """
    Extract listings data from local data/raw directory,
    with performance logging (matches reference pattern).
    """
    try:
        start_time = timeit.default_timer()
        dfs = extract_listings_execution()
        extract_time = timeit.default_timer() - start_time

        logger.info(
            f"Extracted {len(dfs)} datasets in {extract_time:.2f}s ({TYPE})"
        )

        for name, df in dfs.items():
            logger.info(f"Dataset '{name}' loaded with shape {df.shape}")

        return dfs

    except Exception as e:
        logger.error(f"Failed to extract datasets: {e}")
        raise


def extract_listings_execution() -> dict[str, pd.DataFrame]:
    """
    Actual extraction logic — no settings object required.
    Everything is built internally just like in the reference.
    """

    # Build raw folder path manually
    project_root = Path(__file__).resolve().parents[2]  # project root
    raw_dir = project_root / "data" / "raw"

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw folder not found: {raw_dir}")

    raw_files = list(raw_dir.iterdir())

    if not raw_files:
        raise FileNotFoundError(f"No files found in raw folder: {raw_dir}")

    logger.info(f"Reading all CSV files inside: {raw_dir}")

    raw_dfs = {}

    for file_path in raw_files:
        if file_path.suffix.lower() != ".csv":
            logger.warning(f"Skipping unsupported filetype: {file_path}")
            continue

        df = pd.read_csv(file_path)
        name = file_path.stem
        raw_dfs[name] = df
        logger.info(f"Loaded file: {file_path.name} with key '{name}'")

        if not raw_dfs:
            raise ValueError(f"No CSV files found in the raw folder")

    return raw_dfs
