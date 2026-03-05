import json
from typing import Any, Dict

import pandas as pd
import jsonschema


def load_schema(path: str) -> Dict[str, Any]:
    """Load a JSON schema from a file path."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data(path: str) -> pd.DataFrame:
    """Load data into a pandas DataFrame. Supports CSV and JSON files based on extension."""
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    elif path.lower().endswith(".json"):
        return pd.read_json(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")


def validate_dataframe(df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate each row of the dataframe against the provided JSON schema.

    Returns a simple report dict containing total records and number of invalid rows.
    """
    total = len(df)
    invalid = 0
    for _, row in df.iterrows():
        # convert to native python types
        data = row.to_dict()
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError:
            invalid += 1
    return {"total": total, "invalid": invalid}
