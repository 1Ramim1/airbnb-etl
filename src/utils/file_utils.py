import os
import pandas as pd

# R


def find_project_root(marker: str = "requirements.txt") -> str:
    """Return the absolute project root by searching upward for a marker file."""
    path = os.path.abspath(os.path.dirname(__file__))

    while True:
        if marker in os.listdir(path):
            return path

        parent = os.path.dirname(path)
        if parent == path:
            break  # reached filesystem root
        path = parent

    raise FileNotFoundError(f"Marker file '{marker}' not found.")


ROOT_DIR = find_project_root()
# INDEXES_PATH = os.path.join(ROOT_DIR, "etl", "sql", "indexes")
# QUERY_PATH = os.path.join(ROOT_DIR, "etl", "sql")


def save_dataframe_to_csv(df: pd.DataFrame, relative_dir: str, filename: str) -> None:
    """Save a DataFrame to a CSV file inside the project directory."""
    output_path = os.path.join(ROOT_DIR, relative_dir)
    os.makedirs(output_path, exist_ok=True)

    file_path = os.path.join(output_path, filename)
    df.to_csv(file_path, index=False)

    print(f"Data saved to {file_path}")
