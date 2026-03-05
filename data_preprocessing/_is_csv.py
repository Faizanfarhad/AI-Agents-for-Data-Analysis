import pandas as pd
from typing import Optional
from pathlib import Path 
import os
from pathlib import Path as p

files = list(p.cwd().joinpath('cleanedDF').glob('*'))


# Helper function (no @tool decorator) - returns DataFrame
def clean_csv_df(path: str, remove_null: Optional[bool] = False) -> pd.DataFrame:
    """
    Clean CSV data: remove duplicates and handle null values.
    Returns the cleaned DataFrame.
    """
    df = pd.read_csv(path)
    if len(df) < 300000:
        df = df.drop_duplicates()
        if remove_null:
            df = df.dropna()
        else:
            df = df.fillna("Unknown")

    #NOTE : for loading around 1.5x faster then loading directly
    chunklist = []
    for chunk in pd.read_csv(path,chunksize=1000):
        chunk = pd.DataFrame(chunk)
        chunk = chunk.drop_duplicates()
        if remove_null:
            chunk = chunk.dropna()
        else:
            chunk = chunk.fillna("Unknown")
        chunklist.append(chunk)

    df = pd.concat(chunklist)
    if not os.path.exists("cleanedDF"):
        os.makedirs("cleanedDF")
    out = f"cleanedDF/{Path(path).stem}_cleaned.csv"
    df.to_csv(out, index=False)
    return out
