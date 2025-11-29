import os
import sys
from config.env_config import setup_env


def main():
    # Get the argument from the run_etl command and set up the environment
    setup_env(sys.argv)
    print(
        f"ETL pipeline run successfully in "
        f"{os.getenv('ENV', 'error')} environment!"
    )


if __name__ == "__main__":
    main()
