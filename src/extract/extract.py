import pandas as pd
from src.extract.extract_listings import extract_listings
from src.utils.logging_utils import setup_logger

logger = setup_logger("extract_data", "extract_data.log")


def extract_data() -> dict[str, pd.DataFrame]:
    """
    Extract all datasets needed for ETL.
    For now: listings only.
    Extend later: multiple datasets.
    """

    try:
        logger.info("Starting data extraction process")

        listings = extract_listings()

        for name, df in listings.items():
            logger.info(f"Extraction dataset - '{name}': {df.shape}")

        return listings

    except Exception as e:
        logger.error(f"Data extraction failed: {e}")
        raise
