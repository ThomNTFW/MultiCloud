import pandas as pd


def get_file(csv_file_path):
    return pd.read_csv(csv_file_path)

