from matplotlib.figure import figaspect
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
from wordcloud import WordCloud
from pathlib import Path


def visualize_dataset(df: pd.DataFrame, profile: dict, output_dir: str | None = None):
    """
    Generate a full suite of visualizations for a dataset using its profile.


    Visuals Needed: 

        Common:
            - Interactions: graphs between columns
            - Correlations: heatmap
            - Missing Values: bar chart of count, nullity matrix for density, 
        Numeric:
            - Histogram / bar chart with bins?
        Category:
            - Horizontal bar chart
        Text:
            - Word cloud

    """

    figures = []
    pairs = profile['interactions'].data['pairs']
    figures.append(plotInteractions(df, profile, pairs, output_dir))

    corr_table = profile['correlations'].data['correlations']
    figures.append(plotHeatmap(df, profile, corr_table, output_dir))

    warnings = profile['warnings'].data['warnings']

    figures.append(plotMissingValues(df, profile, warnings, output_dir))

    columns = profile['columns'].data
    
    for col in columns:
        col_type = columns[col]['type']

        if col_type == 'numeric':
            figures.append(plotNumericColumn(df, profile, col, output_dir))

        if col_type == 'categorical':
            figures.append(plotCategoricalColumn(df, profile, col, output_dir))

        if col_type == 'text':
            figures.append(plotTextColumn(df, profile, col, output_dir))

    
    return figures

def plotInteractions(df, profile, pairs, output_dir):
    """
    Given the pairs of numeric columns to plot, generates scatterplots for each. 
    Sends to output_dir with name "scatter_{col1}_{col2}.png" where col1 and col2 are the column names.
    """
    if not pairs:
        return []

    figures = []

    for col1, col2 in pairs:
        # Skip if columns missing
        if col1 not in df.columns or col2 not in df.columns:
            continue

        s1 = df[col1]
        s2 = df[col2]

        # Drop rows where either is missing
        df_pair = (
            pd.concat([s1, s2], axis=1)
            .dropna()
        )

        if df_pair.empty:
            continue

        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(
            x=df_pair.iloc[:, 0],
            y=df_pair.iloc[:, 1],
            ax=ax,
            color="steelblue"
        )

        ax.set_xlabel(col1)
        ax.set_ylabel(col2)
        ax.set_title(f"Scatterplot: {col1} vs {col2}")

        # Deterministic filename
        fname = f"scatter_{col1}_{col2}"

        _handle_output(fig, output_dir, fname)
        figures.append(fig)
    return figures

def plotHeatmap(df, profile, correlations, output_dir):
    """
    Given a correlation table, generates a heatmap of the correlations.
    """
    if correlations is None or correlations.empty:
        return None

    # Ensure numeric dtype for plotting
    corr = correlations.astype(float)

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        corr,
        ax=ax,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        annot=False,
        square=True,
        cbar_kws={"shrink": 0.75}
    )

    ax.set_title("Correlation Heatmap")

    # Deterministic filename
    fname = "correlation_heatmap"

    _handle_output(fig, output_dir, fname)
    return fig

def plotMissingValues(df, profile, warnings, output_dir):

    columns = profile['columns'].data
    num_rows = profile['summary'].data['rows']

    missing_dict = {}

    for col in columns: 
        if "missing" in warnings[col]:
            missing_dict[col] = int(warnings[col]["missing"].split()[0])
    
    if not missing_dict:
        return None

   
    fig1 = plotMissingBarChart(columns, num_rows, missing_dict, output_dir)
    fig2 = plotMissingMatrix(df, columns, num_rows, profile, output_dir)
    return fig1, fig2

def plotMissingBarChart(columns, num_rows, missing_dict, output_dir):
    """
    Given the warnings indicating which columns have missing values,
    generates a bar chart of the count of non-missing values per column.
    """
    

    non_missing_counts = []
    col_names = []

    for col in columns:
        missing = missing_dict.get(col, 0)
        non_missing = num_rows - missing
        non_missing_counts.append(non_missing)
        col_names.append(col)

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.barplot(
        x=col_names,
        y=non_missing_counts,
        ax=ax,
        color="steelblue"
    )

    ax.set_title("Non-Missing Values per Column")
    ax.set_ylabel("Count of Non-Missing Values")
    ax.set_xlabel("Columns")

    # Rotate labels for readability
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

    # Deterministic filename
    fname = "missing_barchart"

    _handle_output(fig, output_dir, fname)
    return fig

def plotMissingMatrix(df, columns, n_rows, profile, output_dir):
    
    if df.empty:
        return None

    n_cols = len(columns)

    fig, ax = plt.subplots(figsize=(max(10, n_cols * 0.3), 10))

    bar_width = 0.8  # adjust thickness here

    for i, col in enumerate(columns):
        col_data = df[col]
        missing_mask = col_data.isna()

        for row_idx, is_missing in enumerate(missing_mask):
            color = "lightgray" if is_missing else "steelblue"

            # Rectangle covering exactly one row
            rect = Rectangle(
                (i - bar_width/2, row_idx),   # (x, y)
                bar_width,                    # width
                1,                            # height
                facecolor=color,
                edgecolor=color
            )
            ax.add_patch(rect)

    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(0, n_rows)

    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(columns, rotation=45, ha="right")
    
    ax.set_title("Missing Values Matrix")

    fig.tight_layout()

    fname = "missing_matrix_bars"
    _handle_output(fig, output_dir, fname)

    return fig

def plotNumericColumn(df, profile, col, output_dir):
    """
    Given a numeric column, generates a histogram of the values.
    """
    if col not in df.columns:
        return None

    series = df[col].dropna()
    if series.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.histplot(
        series,
        bins=30,
        kde=False,
        color="steelblue",
        ax=ax
    )

    ax.set_title(f"Histogram of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Frequency")

    fname = f"hist_{col}"
    _handle_output(fig, output_dir, fname)

    return fig

def plotCategoricalColumn(df, profile, col, output_dir):
    """
    Given a categorical column, generates a horizontal bar chart of the value counts.
    """
    if col not in df.columns:
        return None

    series = df[col].dropna()
    if series.empty:
        return None

    # Cardinality-aware cap (consistent with your other categorical plots)
    col_profile = profile.get("columns", {}).get(col, {})
    cardinality = col_profile.get("cardinality")
    max_categories = 20 if cardinality != "high" else 50

    counts = series.value_counts().head(max_categories)

    fig, ax = plt.subplots(figsize=(10, max(4, len(counts) * 0.4)))

    sns.barplot(
        x=counts.values,
        y=counts.index.astype(str),
        ax=ax,
        color="steelblue",
        orient="h"
    )

    ax.set_title(f"Top Categories in {col}")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Category")

    fname = f"cat_{col}"
    _handle_output(fig, output_dir, fname)

    return fig

def plotTextColumn(df, profile, col, output_dir):
    """
    Given a text column, generates a word cloud of the most common words. 
    """
    if col not in df.columns:
        return None

    series = df[col].dropna().astype(str)
    if series.empty:
        return None

    # Tokenize text (simple whitespace split)
    words = []
    for t in series:
        words.extend(t.lower().split())

    if not words:
        return None

    # Count frequencies
    from collections import Counter
    counts = Counter(words)

    # Build word cloud from frequencies
    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        colormap="Blues",
        max_words=200
    ).generate_from_frequencies(counts)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(f"Word Cloud for {col}")

    fname = f"wordcloud_{col}"
    _handle_output(fig, output_dir, fname)

    return fig

def _handle_output(fig, output_dir, name: str):
    """Save or show the figure depending on output_dir."""
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(f"{output_dir}/{name}.png", bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()