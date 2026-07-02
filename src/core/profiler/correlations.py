import numpy as np
import pandas as pd
from scipy.stats import pointbiserialr, chi2_contingency
from .base import ProfilerComponent, SectionResult, register_component

class CorrelationsComponent(ProfilerComponent):

    name = "correlations"

    def compute(self, df, profile):

        all_cols = profile["columns"].data

        corr_table = pd.DataFrame(index=all_cols, columns=all_cols, dtype=float)

        for col1 in all_cols:
            for col2 in all_cols:
                corr_table.loc[col1, col2] = universal_corr(df[col1], df[col2])

        return SectionResult(
            name = self.name,
            data = {
                    "correlations": corr_table
                }
            )

def cramers_v(x, y):
    """Cramér's V for categorical-categorical."""
    confusion = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion)[0]
    n = confusion.sum().sum()
    r, k = confusion.shape
    return np.sqrt(chi2 / (n * (min(r, k) - 1)))


def correlation_ratio(categories, values):
    """Correlation ratio (eta) for categorical-numeric."""
    cat = pd.Categorical(categories)
    groups = [values[cat == c] for c in cat.categories]
    means = np.array([g.mean() for g in groups])
    sizes = np.array([len(g) for g in groups])
    overall_mean = values.mean()

    numerator = np.sum(sizes * (means - overall_mean)**2)
    denominator = np.sum((values - overall_mean)**2)
    return np.sqrt(numerator / denominator) if denominator != 0 else 0.0


def universal_corr(x, y):
    """Universal correlation function for any dtype combination."""

    # Drop NA
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    x = df["x"]
    y = df["y"]

    # Identify types
    x_num = pd.api.types.is_numeric_dtype(x)
    y_num = pd.api.types.is_numeric_dtype(y)

    # Case 1: numeric × numeric → Pearson
    if x_num and y_num:
        return x.corr(y)

    # Case 2: numeric × categorical
    if x_num and not y_num:
        if y.nunique() == 2:
            encoded = pd.factorize(y)[0]
            corr, _ = pointbiserialr(encoded, x)
            return corr
        else:
            return correlation_ratio(y, x)

    # Case 3: categorical × numeric
    if not x_num and y_num:
        if x.nunique() == 2:
            encoded = pd.factorize(x)[0]
            corr, _ = pointbiserialr(encoded, y)
            return corr
        else:
            return correlation_ratio(x, y)

    # Case 4: categorical × categorical → Cramér's V
    return cramers_v(x, y)



register_component(CorrelationsComponent())