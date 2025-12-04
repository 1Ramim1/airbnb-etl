import os
import sys
from pathlib import Path
from config.env_config import setup_env
from src.extract.extract import extract_data
from src.utils.logging_utils import setup_logger
from src.transform.transform_data import transform_data


def main():
    # Get the argument from the run_etl command and set up the environment

    # logger
    logger = setup_logger("etl_pipeline", "etl_pipeline.log")

    setup_env(sys.argv)
    print(
        f"ETL pipeline run successfully in "
        f"{os.getenv('ENV', 'error')} environment!"
    )

    try:
        logger.info("Starting extraction phase")
        extracted_data = extract_data()
        logger.info("Data extraction phase completed")

        # proof of confirmation
        print(f"\nExtracted data terminal previews:")
        for name, df in extracted_data.items():
            print(f"\nDataset: {name}")
            print(df.head())

        for name, df in extracted_data.items():
            logger.info(
                f"Dataset '{name}' Extraction returned: {df.shape[0]} rows and "
                f"{df.shape[1]} columns"
            )

        # Transformation phase
        logger.info("Beginning data transformation phase")
        transformed_data = transform_data(
            extracted_data['dirty_detailed_listings_data'])
        # Create output directory and file
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("ETL pipeline successfully completed")

    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        print(f"ETL Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
