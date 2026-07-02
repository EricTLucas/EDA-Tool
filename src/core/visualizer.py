from matplotlib.figure import figaspect
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
    column_summary(df, profile, output_dir)
    sample_entry(df, profile, output_dir)
    
    sig_columns = []
    index_column = None

    # Column-level plots driven by profile
    for col in df.columns:
        series = df[col]
        col_profile = profile["columns"].get(col, {})

        # Skip ID-like or constant columns based on profile
        if col_profile.get("cardinality") == "id":
            if _is_numeric_dtype(col_profile.get("dtype", str(series.dtype))) and index_column == None:
                df.index.name = col
                index_column = col
            continue
        if col_profile.get("num_unique") == 1:
            continue

        dtype = col_profile.get("dtype", str(series.dtype))
        
        cardinality = col_profile.get("cardinality")

        if _is_numeric_dtype(dtype):
            plot_numeric_distribution(series, col_profile, output_dir)
            sig_columns.append([col, dtype])

        elif _is_categorical_dtype(dtype, cardinality):
            plot_categorical_distribution(series, col_profile, output_dir)
            sig_columns.append([col, dtype])

        elif _is_datetime_dtype(dtype):
            plot_datetime_distribution(series, col_profile, output_dir)
            sig_columns.append([col, dtype])
        
    numeric = ["int", "float", "number", "float64"]
    
    for i in range(len(sig_columns)-1):
        if sig_columns[i+1][1] == "str":
            single_column_summary(df[sig_columns[i+1][0]], profile["columns"].get(sig_columns[i+1][0], {}), output_dir)

        for j in range(i+1, len(sig_columns)):
            col, dtype = sig_columns[i]
            
            col2, dtype2 = sig_columns[j]
    
            if dtype in numeric and dtype2 in numeric:
                plot_scatterplot(df[col], df[col2], output_dir)
            elif (dtype == "str" and dtype2 in numeric) or (dtype2 == "str" and dtype in numeric):
                if dtype == "str":
                    plot_boxplot_by_category(df[col], df[col2], output_dir)
                else:
                    plot_boxplot_by_category(df[col2], df[col], output_dir)
            elif dtype == "str" and dtype2 == "str":
                plot_mosaic(df[col], df[col2], 
                            profile["columns"].get(col, {}), profile["columns"].get(col2, {}), output_dir)
    
    if index_column is not None:
        for col, dtype in sig_columns:
            if dtype in numeric:
                plot_scatterplot(df[index_column], df[col], output_dir)

        if profile['num_missing'] > 0:
            plot_missing_by_index(df, index_column, output_dir)

    return None

def describe_dataset(df: pd.DataFrame, profile: dict, output_dir=None):
    """Simple text summary of dataset."""
    shape = profile.get("shape", df.shape)
    fig, ax = plt.subplots(figsize=(6, 1))
    text = f"Dataset Shape: {shape[0]} rows x {shape[1]} columns\n"
    text = text + f"Number of Duplicates: {str(profile['num_duplicates'])}\n" + f"Number of Missing Values: {str(profile['num_missing'])}"

    ax.text(0.5, 0.5, text,
            ha='center', va='center', fontsize=12)
    ax.axis('off')
    _handle_output(fig, output_dir, "Dataset_Info")
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
    _handle_output(fig, output_dir, "Sample_Entry")
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

    _handle_output(fig, output_dir, "Column_Summary")
    return fig

def plot_missing_by_index(df: pd.DataFrame, index_col: str, output_dir=None):
    """
    Plot missing vs non-missing values for each NON-index column across the index.
    Each column gets a horizontal line (y = column index),
    and each row gets a dot: blue = present, red = missing.
    """

    if df.empty:
        return None

    # Ensure index_col is the index
    if df.index.name != index_col:
        df = df.set_index(index_col)

    # Skip the index column itself
    columns = [c for c in df.columns if c != index_col]
    n_cols = len(columns)

    if n_cols == 0:
        return None

    fig, ax = plt.subplots(figsize=(12, max(4, n_cols * 0.3)))

    for i, col in enumerate(columns):
        col_data = df[col]

        # Boolean mask: True = missing
        missing_mask = col_data.isna()

        # x = index values
        x_vals = df[index_col].values

        # y = constant line for this column
        y_vals = np.full_like(x_vals, i, dtype=float)

        # Present values
        ax.scatter(
            x_vals[~missing_mask],
            y_vals[~missing_mask],
            color="steelblue",
            s=10,
            label="Present" if i == 0 else None
        )

        # Missing values
        ax.scatter(
            x_vals[missing_mask],
            y_vals[missing_mask],
            color="red",
            s=10,
            label="Missing" if i == 0 else None
        )

    # Formatting
    ax.set_yticks(range(n_cols))
    ax.set_yticklabels(columns)
    ax.set_xlabel(index_col)
    ax.set_title("Missing Values by Index")

    ax.legend(loc="upper right")

    _handle_output(fig, output_dir, "Missing_By_Index")
    return fig

def single_column_summary(series: pd.Series, col_profile: dict, output_dir=None):
    print(col_profile)
    fig, ax = plt.subplots(figsize=(6, 1))
    text = "Something\n"

    ax.text(0.5, 0.5, text,
            ha='center', va='center', fontsize=12)
    ax.axis('off')

    _handle_output(fig, output_dir, f"{series.name}_Summary")
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

    _handle_output(fig, output_dir, f"{series.name}_Distribution")
    return fig




def plot_boxplot(series: pd.Series, col_profile: dict, output_dir=None):
    """Boxplot for numeric columns."""
    fig, ax = plt.subplots(figsize=(6, 2))
    sns.boxplot(x=series.dropna(), ax=ax, color="orange")
    ax.set_title(f"Boxplot of {series.name}")

    _handle_output(fig, output_dir, f"{series.name}_Boxplot")
    return fig

def plot_categorical_distribution(series: pd.Series, col_profile: dict, output_dir=None):
    """Pie chart of category frequencies."""
    
    cardinality = col_profile.get("cardinality")
    max_categories = 20 if cardinality != "high" else 50

    counts = series.value_counts(dropna=True).head(max_categories)

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.pie(
        counts.values,
        labels=counts.index.astype(str),
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False
    )

    ax.set_title(f"Top Categories in {series.name}")

    _handle_output(fig, output_dir, f"{series.name}_Categories")
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

    _handle_output(fig, output_dir, f"{series.name}_Datetime")
    return fig

def plot_scatterplot(series1: pd.Series, series2: pd.Series, output_dir=None):
    """
    Create a scatterplot between two numeric Series.
    Both Series must be aligned by index.
    """

    # Drop rows where either value is missing
    s1 = series1.dropna()
    s2 = series2.dropna()
    df = pd.concat([s1, s2], axis=1).dropna()

    if df.empty:
        return None

    xname = series1.name or "x"
    yname = series2.name or "y"

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax, color="steelblue")

    ax.set_xlabel(xname)
    ax.set_ylabel(yname)
    ax.set_title(f"Scatterplot: {xname} vs {yname}")

    _handle_output(fig, output_dir, f"Scatter_{xname}_vs_{yname}")
    return fig

def plot_boxplot_by_category(cat_series: pd.Series, num_series: pd.Series, output_dir=None):
    """
    Create a boxplot comparing a categorical Series to a numeric Series.
    Both Series must be aligned by index.
    """

    # Drop rows where either value is missing
    df = pd.concat([cat_series, num_series], axis=1).dropna()
    if df.empty:
        return None

    cat_name = cat_series.name or "category"
    num_name = num_series.name or "value"

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(x=df.iloc[:, 0], y=df.iloc[:, 1], ax=ax, color="skyblue")

    ax.set_xlabel(cat_name)
    ax.set_ylabel(num_name)
    ax.set_title(f"Boxplot: {num_name} by {cat_name}")

    # Save or show
    _handle_output(fig, output_dir, f"Boxplot_{num_name}_by_{cat_name}")
    return fig

def plot_mosaic(series1: pd.Series, series2: pd.Series, profile1: dict, profile2: dict, output_dir=None):
    return 

def _is_numeric_dtype(dtype_str: str) -> bool:
    return dtype_str in ["int", "float", "number", "float64"]


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