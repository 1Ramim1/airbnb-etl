import pandas as pd


def load_csv(name_of_file: str):
    return pd.read_csv(name_of_file)
