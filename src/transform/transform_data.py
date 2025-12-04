import pandas as pd
from src.transform.clean_listings import clean_listings
from src.utils.logging_utils import setup_logger
from src.utils.file_utils import save_dataframe_to_csv
from src.transform.transform_listings import transform_listings

logger = setup_logger("transform_data", "transform_data.log")

OUTPUT_DIR = "data/processed"
FILE_NAME = "cleaned_listings.csv"


def transform_data(data) -> pd.DataFrame:
    try:
        # here we clean the airbnb listings dataset
        logger.info("Starting data transformation process:")
        data = clean_listings(data)
        data = transform_listings(data)
        logger.info("Transaction data successfully cleaned.")

        save_dataframe_to_csv(data, OUTPUT_DIR, FILE_NAME)

        return data

    except Exception as e:
        logger.error(f"Data transformation failed: {str(e)}")
        raise
