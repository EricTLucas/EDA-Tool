import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
from wordcloud import WordCloud
from pathlib import Path
matplotlib.use("Agg")

def visualize_dataset(df: pd.DataFrame, profile: dict, output_dir: str):
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
    sample = profile['interactions'].data['sampled']
    figures.append(plotInteractions(df, profile, pairs, sample, output_dir))

    corr_table = profile['correlations'].data
    figures.append(plotHeatmap(df, profile, corr_table, output_dir))

    warnings = profile['warnings'].data

    figures.append(plotMissingValues(df, profile, warnings, output_dir))

    columns = profile['columns'].data
    
    for col in columns:
        col_type = columns[col]['type']

        if col_type == 'numeric':
            figures.append(plotNumericColumn(df, profile, col, output_dir))

        if col_type == 'category':
            figures.append(plotCategoricalColumn(df, profile, col, output_dir))

        if col_type == 'text':
            figures.append(plotTextColumn(df, profile, col, output_dir))

    
    return figures

def plotInteractions(df, profile, pairs, sample, output_dir):
    """
    Given the pairs of numeric columns to plot, generates scatterplots for each
    using the SAMPLE provided (not the full df).
    Saves each figure to output_dir using:
        scatter_{col1}_{col2}.png
    """

    if not pairs:
        return []

    figures = []

    for col1, col2 in pairs:
        # Determine sample key
        # You can choose either tuple keys or string keys; support both.
        key_tuple = (col1, col2)
        key_str = f"{col1}|{col2}"

        # Retrieve sample for this interaction
        if key_tuple in sample:
            df_pair = sample[key_tuple]
        elif key_str in sample:
            df_pair = sample[key_str]
        else:
            # No sample available → skip
            continue


        # Defensive: ensure columns exist in sample
        if col1 not in df_pair.columns or col2 not in df_pair.columns:
            continue

        # Plot
        fig, ax = plt.subplots(figsize=(9, 6))
        if col1 == col2:
            x_vals = df_pair[col1].iloc[:, 0]   # first copy
            y_vals = df_pair[col2].iloc[:, 1]   # second copy
        else:
            x_vals = df_pair[col1]
            y_vals = df_pair[col2]

        sns.scatterplot(
            x=x_vals,
            y=y_vals,
            ax=ax,
            color="steelblue"
        )

        ax.set_xlabel(col1)
        ax.set_ylabel(col2)
        ax.set_title(f"Scatterplot (sample): {col1} vs {col2}")

        # Deterministic filename
        fname = f"scatter_{col1}_vs_{col2}"

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
        cmap="coolwarm_r",
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
            missing_dict[col] = columns[col]["num_missing"]
    
    if not missing_dict:
        return None

   
    fig1 = plotMissingBarChart(columns, num_rows, missing_dict, output_dir)
    fig2 = plotMissingMatrix(df, columns, num_rows, missing_dict, profile, output_dir)
    return fig1, fig2


def plotMissingBarChart(columns, num_rows, missing_dict, output_dir):
    """
    Generates a bar chart of non-missing counts per column.
    - Fixed height ~300px
    - Y-axis shows fractional ticks: 0.2, 0.4, ..., 1.0
    - Count labels displayed above each bar
    """

    non_missing_counts = []
    col_names = []
    n_cols = len(columns)

    for col in columns:
        missing = missing_dict.get(col, 0)
        non_missing = num_rows - missing
        non_missing_counts.append(non_missing)
        col_names.append(col)

    fig, ax = plt.subplots(figsize=(12, 6))

    for spine in ax.spines.values():
        spine.set_visible(False)

   
    #ax.tick_params(bottom=False, left=False)


    sns.barplot(
        x=col_names,
        y=non_missing_counts,
        ax=ax,
        color="steelblue"
    )

    ax.set_title("")
    ax.set_ylabel("")
    ax.set_xlabel("")

    # --- Y-axis ticks: 0.2, 0.4, ..., 1.0 ---
    frac_ticks = [i/5 for i in range(1, 6)]  # 0.2 → 1.0
    ax.set_yticks([t * num_rows for t in frac_ticks])
    ax.set_yticklabels([f"{t:.1f}" for t in frac_ticks])

    # Rotate labels for readability
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(col_names, rotation=45, ha="right")

    # --- Add count labels above each bar ---
    for i, count in enumerate(non_missing_counts):
        ax.text(
            i, count,                # position
            str(count),              # label
            ha='center', va='bottom',
            fontsize=10,
            color='black'
        )

    # Deterministic filename
    fname = "missing_barchart"
    _handle_output(fig, output_dir, fname)

    return fig

def plotMissingMatrix(df, columns, n_rows, missing_dict, profile, output_dir):
    
    if df.empty:
        return None

    n_cols = len(columns)

    fig, ax = plt.subplots(figsize=(max(10, n_cols * 0.3), 10))
    for spine in ax.spines.values():
        spine.set_visible(False)

    bar_width = 0.8  # adjust thickness here

    for i, col in enumerate(columns):

        # If column NOT in missing_dict → draw one solid blue bar
        if col not in missing_dict:
            rect = Rectangle(
                (i - bar_width/2, 0),   # x, y
                bar_width,              # width
                n_rows,                 # full height
                facecolor="steelblue",
                edgecolor="steelblue"
            )
            ax.add_patch(rect)
            continue

        # Otherwise: row-by-row missingness visualization
        col_data = df[col]
        missing_mask = col_data.isna()

        for row_idx, is_missing in enumerate(missing_mask):
            color = "lightgray" if is_missing else "steelblue"

            rect = Rectangle(
                (i - bar_width/2, row_idx),
                bar_width,
                1,
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

    max_categories = 20 

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
    # TEST AT SOME POINT
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
        plt.close(fig)