import os
import sys
import subprocess
from pathlib import Path
from config.env_config import setup_env
from src.extract.extract import extract_data
from src.utils.logging_utils import setup_logger
from src.transform.transform_data import transform_data


def open_streamlit():
    logger = setup_logger("open_streamlit", "etl_pipeline.log")

    project_root = Path(__file__).resolve().parents[1]
    streamlit_path = project_root / "streamlit" / "app.py"

    if not streamlit_path.exists():
        logger.error(f"Streamlit path not found on {streamlit_path}")
        return None

    process = subprocess.Popen(
        ["streamlit", "run", str(streamlit_path)],
        stdout=None,
        stderr=None
    )
    logger.info("Streamlit launch success!")
    return process


def main():
    # logger
    logger = setup_logger("etl_pipeline", "etl_pipeline.log")

    # FORCE the environment to dev
    setup_env(["run_app", "dev"])
    print(f"ETL pipeline running in {os.getenv('ENV')} environment!")

    try:
        logger.info("Starting extraction phase")
        extracted_data = extract_data()
        logger.info("Data extraction phase completed")

        # Proof of extraction
        print("\nExtracted data terminal previews:")
        for name, df in extracted_data.items():
            print(f"\nDataset: {name}")
            print(df.head())

        for name, df in extracted_data.items():
            logger.info(
                f"Dataset '{name}' returned: {df.shape[0]} rows x {df.shape[1]} cols"
            )

        # Transformation phase
        logger.info("Beginning data transformation phase")
        transformed_data = transform_data(
            extracted_data['detailed_listings_data']
        )

        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("ETL pipeline successfully completed")

        logger.info("Starting Streamlit...")
        open_streamlit()

    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        print(f"ETL Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
