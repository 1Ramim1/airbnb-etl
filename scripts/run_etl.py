import os
import sys
from config.env_config import setup_env
from src.extract.extract import extract_data
from src.utils.logging_utils import setup_logger


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
        print(f"\nExtracde data terminal preview:{extracted_data.head()}\n")

        logger.info(
            f"Extraction returned {extracted_data.shape[0]} rows and "
            f"{extracted_data.shape[1]} columns"
        )

        logger.info("ETL pipeline successfully completed")

    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        print(f"ETL Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
