
import pandas as pd
from .cohort import Spiredf

def get_num_uniq_pts(df):
    return df[Spiredf.ptid].nunique()

def series_type(s: pd.Series) -> str:
    """
    Classify a pandas Series as 'numeric', 'boolean', or 'string'.
    """
    # Drop missing values for inspection
    s_nonnull = s.dropna()

    if s_nonnull.empty:
        return "string"  # default for empty / all-NA

    # Boolean (includes pandas BooleanDtype)
    if pd.api.types.is_bool_dtype(s):
        return "boolean"

    # Numeric dtypes
    if pd.api.types.is_numeric_dtype(s):
        return "numeric"

    # Object / string columns: inspect values
    if pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s):
        # Check boolean-like strings
        bool_like = {"true", "false", "0", "1", "yes", "no"}
        lowered = s_nonnull.astype(str).str.lower().unique()
        if set(lowered).issubset(bool_like):
            return "boolean"

        # Check numeric-like strings
        try:
            pd.to_numeric(s_nonnull, errors="raise")
            return "numeric"
        except Exception:
            return "string"

    return "string"
