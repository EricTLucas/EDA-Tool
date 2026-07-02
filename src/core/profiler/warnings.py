from .base import ProfilerComponent, SectionResult, register_component

class WarningsComponent(ProfilerComponent):
    name = "warnings"

    def compute(self, df, profile):
        warnings = {}

        corrs = profile["correlations"].data["correlations"]

        cols = profile["columns"].data

        for col in cols:
            warnings[col] =  getWarnings(cols[col], cols[col]["type"]) 

            row = corrs.loc[col]

            for other_col, value in row.items():

                if abs(value) > 0.75 and other_col != col:
                    warnings[col]["high_correlation"] = f"High correlation with {other_col} ({value:.2f})"

        return SectionResult(
            name=self.name,
            data={
                "warnings": warnings
            }
        )


def getWarnings(col_profile, type: str) -> dict:
    """
    Generate warnings based on the column profile and type.
    Possible warnings include: 
    - Missing: Any missing values in the data
    - Uniform Distribution: 
    - Unique: All values are unique (e.g., ID columns)
    - High Correlation: High correlation with another column
    
    Numeric Warnings:
    - Zeros: Inclusion of zeros in the data
    - Negatives: Inclusion of negative values in the data
    - Infinities: Inclusion of infinite values in the data
    """
    col_warnings = {}

    if col_profile["num_missing"] > 0:
        number_missing = col_profile["num_missing"]
        pct_missing = col_profile["pct_missing"]
        col_warnings["missing"] = f"{number_missing} missing values ({pct_missing:.2%})"

    if col_profile["pct_unique"] == 1.0: 
        col_warnings["unique"] = "All values are unique (possible ID column)"

    if type == "numeric":
        if col_profile["num_zeros"] > 0:
            col_warnings["zeros"] = f"{col_profile["num_zeros"]} zeros"

        if col_profile["num_neg"] > 0:
            col_warnings["negatives"] = f"{col_profile["num_neg"]} negative values"

        if col_profile["num_infinity"] > 0:
            col_warnings["infinity"] = f"{col_profile["num_infinity"]} infinite values"

        if col_profile["uniform_dist"] == True:
            col_warnings["uniform_dist"] = "Data appears to be uniformly distributed"

        return col_warnings
    elif type == "category":
        return col_warnings
    elif type == "text":

        return col_warnings


register_component(WarningsComponent())