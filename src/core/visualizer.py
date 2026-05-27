import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def visualize_dataset(df: pd.DataFrame, profile: dict, output_dir: str | None = None):
    """
    Generate a full suite of visualizations for a dataset using its profile.
    If output_dir is provided, save plots instead of showing them.
    """
    # Dataset-level plots
    describe_dataset(df, profile, output_dir)
    sample_entry(df, profile, output_dir)
    plot_missing_values_from_profile(profile, output_dir)
    column_summary(df, profile, output_dir)

    # Column-level plots driven by profile
    for col in df.columns:
        series = df[col]
        col_profile = profile["columns"].get(col, {})

        # Skip ID-like or constant columns based on profile
        if col_profile.get("cardinality") == "id":
            continue
        if col_profile.get("num_unique") == 1:
            continue

        dtype = col_profile.get("dtype", str(series.dtype))
        cardinality = col_profile.get("cardinality")

        if _is_numeric_dtype(dtype):
            plot_numeric_distribution(series, col_profile, output_dir)
            plot_boxplot(series, col_profile, output_dir)

        elif _is_categorical_dtype(dtype, cardinality):
            plot_categorical_distribution(series, col_profile, output_dir)

        elif _is_datetime_dtype(dtype):
            plot_datetime_distribution(series, col_profile, output_dir)
        # missing values by index / patterns
        # comparisons between numeric columns (scatter, correlation), categorical columns (mosaic), numeric vs categorical (boxplot, violin)

    return None


def plot_missing_values_from_profile(profile: dict, output_dir=None):
    """Bar chart of missing values per column using profile stats."""
    missing = profile.get("missing_by_column", {})
    if not missing:
        return None
    if all(v == 0 for v in missing.values()):
        return None

    s = pd.Series(missing)

    fig, ax = plt.subplots(figsize=(10, 4))
    s.plot(kind="bar", ax=ax, color="steelblue")
    ax.set_title("Missing Values per Column")
    ax.set_ylabel("Count")

    _handle_output(fig, output_dir, "missing_values")
    return fig

def describe_dataset(df: pd.DataFrame, profile: dict, output_dir=None):
    """Simple text summary of dataset."""
    shape = profile.get("shape", df.shape)
    fig, ax = plt.subplots(figsize=(6, 1))
    text = f"Dataset Shape: {shape[0]} rows x {shape[1]} columns\n"
    text = text + f"Number of Duplicates: {str(profile['num_duplicates'])}\n" + f"Number of Missing Values: {str(profile['num_missing'])}"

    ax.text(0.5, 0.5, text,
            ha='center', va='center', fontsize=12)
    ax.axis('off')
    _handle_output(fig, output_dir, "dataset_info")
    return fig

def sample_entry(df: pd.DataFrame, profile: dict, output_dir=None):
    """Render a sample entry as a table-like text block with wrapping."""
    if df.empty:
        return None

    df = df.iloc[:, :16]
    row = df.sample(1).iloc[0]

    values = [("" if pd.isna(v) else str(v)) for v in row.tolist()]
    columns = df.columns.tolist()

    wrapped_tables = []
    chunk_size = 8

    for start in range(0, len(columns), chunk_size):
        end = start + chunk_size
        cols_chunk = columns[start:end]
        vals_chunk = values[start:end]

        
        col_widths = [
            max(len(str(col)), len(val))
            for col, val in zip(cols_chunk, vals_chunk)
        ]

       
        header = " | ".join(
            col.ljust(width) for col, width in zip(cols_chunk, col_widths)
        )

        separator = "-+-".join("-" * width for width in col_widths)

        value_row = " | ".join(
            val.ljust(width) for val, width in zip(vals_chunk, col_widths)
        )

        wrapped_tables.append(f"{header}\n{separator}\n{value_row}")

    # Combine all wrapped tables with spacing
    table_str = "\n\n".join(wrapped_tables)

    # Add title
    final_text = f"Sample Entry\n\n{table_str}"

    # Render inside a matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.text(
        0.5, 0.5,
        final_text,
        ha="center",
        va="center",
        family="monospace",
        fontsize=10,
        wrap=True
    )
    ax.axis("off")
    _handle_output(fig, output_dir, "sample_entry")
    return fig

def column_summary(df: pd.DataFrame, profile: dict, output_dir=None):
    """
    Render a table-like summary of:
    - column name
    - dtype (from profile)
    - missing count (from profile)
    """

    missing = profile.get("missing_by_column", {})
    col_profiles = profile.get("columns", {})

    # Build rows in DataFrame column order
    rows = []
    for col in df.columns:
        dtype = col_profiles.get(col, {}).get("dtype", "unknown")
        miss = missing.get(col, 0)
        rows.append((col, dtype, miss))

    # Compute column widths for alignment
    name_w = max(len("Column"), max(len(r[0]) for r in rows))
    dtype_w = max(len("Dtype"), max(len(str(r[1])) for r in rows))
    miss_w = max(len("Missing"), max(len(str(r[2])) for r in rows))

    # Header
    header = (
        f"{'Column'.ljust(name_w)} | "
        f"{'Dtype'.ljust(dtype_w)} | "
        f"{'Missing'.rjust(miss_w)}"
    )
    separator = (
        f"{'-'*name_w}-+-{'-'*dtype_w}-+-{'-'*miss_w}"
    )

    # Body rows
    body_lines = []
    for col, dtype, miss in rows:
        body_lines.append(
            f"{col.ljust(name_w)} | "
            f"{dtype.ljust(dtype_w)} | "
            f"{str(miss).rjust(miss_w)}"
        )

    # Combine into final text block
    table_text = "\n".join([header, separator] + body_lines)

    # Render inside a matplotlib figure
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.text(
        0.5, 0.5,
        table_text,
        ha="center",
        va="center",
        family="monospace",
        fontsize=10,
        wrap=False
    )
    ax.axis("off")

    _handle_output(fig, output_dir, "column_summary")
    return fig


def plot_numeric_distribution(series: pd.Series, col_profile: dict, output_dir=None):
    """Histogram + KDE for numeric columns."""
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(series.dropna(), kde=True, ax=ax, color="teal")

    mean = col_profile.get("mean")
    if mean is not None:
        ax.axvline(mean, color="red", linestyle="--", label=f"mean={mean:.2f}")
        ax.legend()

    ax.set_title(f"Distribution of {series.name}")

    _handle_output(fig, output_dir, f"{series.name}_distribution")
    return fig


def plot_boxplot(series: pd.Series, col_profile: dict, output_dir=None):
    """Boxplot for numeric columns."""
    fig, ax = plt.subplots(figsize=(6, 2))
    sns.boxplot(x=series.dropna(), ax=ax, color="orange")
    ax.set_title(f"Boxplot of {series.name}")

    _handle_output(fig, output_dir, f"{series.name}_boxplot")
    return fig

def plot_categorical_distribution(series: pd.Series, col_profile: dict, output_dir=None):
    """Bar chart of category frequencies."""
    # Use cardinality info to cap number of categories
    cardinality = col_profile.get("cardinality")
    max_categories = 20 if cardinality != "high" else 50

    counts = series.value_counts(dropna=True).head(max_categories)

    fig, ax = plt.subplots(figsize=(10, 4))
    counts.plot(kind="bar", ax=ax, color="purple")
    ax.set_title(f"Top Categories in {series.name}")
    ax.set_ylabel("Frequency")

    _handle_output(fig, output_dir, f"{series.name}_categories")
    return fig

def plot_datetime_distribution(series: pd.Series, col_profile: dict, output_dir=None):
    """Line plot of datetime counts."""
    s = series.dropna()
    if s.empty:
        return None

    counts = s.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 4))
    counts.plot(ax=ax)
    ax.set_title(f"Time Distribution of {series.name}")
    ax.set_ylabel("Count")

    _handle_output(fig, output_dir, f"{series.name}_datetime")
    return fig

def _is_numeric_dtype(dtype_str: str) -> bool:
    return any(k in dtype_str for k in ["int", "float", "number"])


def _is_datetime_dtype(dtype_str: str) -> bool:
    return "datetime" in dtype_str


def _is_categorical_dtype(dtype_str: str, cardinality: str | None) -> bool:
    if "object" in dtype_str or "string" in dtype_str or "str" in dtype_str:
        return True
    # You could also treat low-cardinality numerics as categorical later
    return False

def _handle_output(fig, output_dir, name: str):
    """Save or show the figure depending on output_dir."""
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(f"{output_dir}/{name}.png", bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()