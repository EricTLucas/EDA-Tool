import pandas as pd
import numpy as np

def profile_dataset(df: pd.DataFrame) -> dict:
    profile = {}

    # --- Dataset-level summary ---
    profile["shape"] = df.shape
    profile["memory_usage"] = int(df.memory_usage(deep=True).sum())
    profile["num_duplicates"] = int(df.duplicated().sum())
    profile["num_missing"] = int(df.isna().sum().sum())
    profile["missing_by_column"] = df.isna().sum().to_dict()

    # --- Column-level summary ---
    columns = {}
    for col in df.columns:
        series = df[col]
        col_profile = {}

        col_profile["dtype"] = str(series.dtype)
        col_profile["num_missing"] = int(series.isna().sum())
        col_profile["pct_missing"] = float(series.isna().mean())
        col_profile["num_unique"] = int(series.nunique(dropna=True))
        col_profile["sample_values"] = series.dropna().unique()[:5].tolist()

        # Numeric stats
        if pd.api.types.is_numeric_dtype(series):
            col_profile["mean"] = float(series.mean())
            col_profile["std"] = float(series.std())
            col_profile["min"] = float(series.min())
            col_profile["max"] = float(series.max())
            col_profile["skew"] = float(series.skew())
            col_profile["kurtosis"] = float(series.kurtosis())

        # Categorical stats
        if isinstance(series.dtype, pd.StringDtype) or isinstance(series.dtype, pd.CategoricalDtype):
            col_profile["top"] = series.mode().iloc[0] if not series.mode().empty else None

        # Datetime stats 
        if isinstance(series.dtype, pd.DatetimeTZDtype):
            col_profile["min"] = str(series.min())
            col_profile["max"] = str(series.max())
             
        # Cardinality classification
        unique = col_profile["num_unique"]
        if unique == df.shape[0]:
            col_profile["cardinality"] = "id"
        elif unique < 20:
            col_profile["cardinality"] = "low"
        elif unique < 1000:
            col_profile["cardinality"] = "medium"
        else:
            col_profile["cardinality"] = "high"

        columns[col] = col_profile

    profile["columns"] = columns

    # --- Correlations (numeric only) ---
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] > 1:
        profile["correlations"] = numeric_df.corr().to_dict()
    else:
        profile["correlations"] = {}

    # --- Warnings ---
    warnings = []
    for col, info in columns.items():
        if info["num_missing"] > df.shape[0] * 0.5:
            warnings.append(f"{col}: more than 50% missing")
        if info["cardinality"] == "id":
            warnings.append(f"{col}: looks like an ID column")
        if info["num_unique"] == 1:
            warnings.append(f"{col}: constant column")

    profile["warnings"] = warnings

    return profile