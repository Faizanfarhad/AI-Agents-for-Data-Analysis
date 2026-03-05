import pandas as pd
from typing import Optional
from data_preprocessing._is_csv import clean_csv_df
from data_preprocessing._is_json import clean_json_df


def execute(file_path: str, remove_null: Optional[bool] = False) -> pd.DataFrame:
    """
    Route file processing based on file format.
    Returns cleaned DataFrame.
    """
    if file_path.endswith('.csv'):
        return clean_csv_df(file_path, remove_null)
    elif file_path.endswith('.json'):
        return clean_json_df(file_path, remove_null)
    elif file_path.endswith('.txt'):
        # For text files, just read with pandas
        df = pd.read_csv(file_path, sep=None, engine='python')
        return df
    else:
        raise ValueError(f"Unsupported file format: {file_path}") 