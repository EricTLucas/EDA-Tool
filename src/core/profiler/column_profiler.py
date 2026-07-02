from .base import ProfilerComponent, SectionResult, register_component
import pandas as pd
import numpy as np
from collections import Counter 

class ColumnProfiler(ProfilerComponent):
    name = "columns"

    def compute(self, df, profile):
        num_rows = df.shape[0]
        
        numeric = ["int","int8", "int16", "int32", 
               "int64", "uint8", "uint16", "float", 
               "uint32", "uint64", "float16", 
               "float32", "float64", "complex64", 
               "complex128", "Int8", "Int16", 
               "Int32", "Int64", "Float32", "Float64"]

        text = ["bool", "boolean", "object", 
                "string", "str", "bytes", 
                "datetime64[ns]", "datetime64[ns, tz]", "timedelta64[ns]",
                "category", "mixed"]

        
        columns = {}



        for col in df.columns:

            series = df[col]
            col_profile = {}

            col_profile["dtype"] = str(series.dtype)

            col_profile["num_missing"] = int(series.isna().sum())
            col_profile["pct_missing"] = col_profile["num_missing"] / num_rows
            col_profile["num_unique"] = int(series.nunique(dropna=True))
            col_profile["pct_unique"] = col_profile["num_unique"] / num_rows
            col_profile["sample_values"] = series.dropna().unique()[:5].tolist()
            col_profile["memory_size"] = int(series.memory_usage(deep=True)) 
            unique = col_profile["num_unique"]
            if unique == df.shape[0]:
                col_profile["cardinality"] = "id"
            elif unique < 20:
                col_profile["cardinality"] = "low"
            elif unique < 1000:
                col_profile["cardinality"] = "medium"
            else:
                col_profile["cardinality"] = "high"

            if col_profile["dtype"] in numeric:
                if col_profile["cardinality"] == "low":
                    col_profile["type"] = "category"
                else:
                    col_profile["type"] = "numeric"
            if col_profile["dtype"] in text:
                if col_profile["cardinality"] == "low":
                    col_profile["type"] = "category"
                else:
                    col_profile["type"] = "text"



            if col_profile["type"] == "numeric":

                # Basic stats
                col_profile["mean"] = float(series.mean())
                col_profile["std"] = float(series.std())
                col_profile["min"] = float(series.min())
                col_profile["max"] = float(series.max())
                col_profile["skew"] = float(series.skew())
                col_profile["kurtosis"] = float(series.kurtosis())

                # Infinity counts
                num_inf = series.isin([float("inf"), float("-inf")]).sum()
                col_profile["num_infinity"] = int(num_inf)
                col_profile["pct_infinity"] = float(num_inf / num_rows)

                # Zero counts
                num_zero = (series == 0).sum()
                col_profile["num_zeros"] = int(num_zero)
                col_profile["pct_zeros"] = float(num_zero / num_rows)

                # Negative counts
                num_neg = (series < 0).sum()
                col_profile["num_neg"] = int(num_neg)
                col_profile["pct_neg"] = float(num_neg / num_rows)

                # Uniform distribution check
                q = np.quantile(series.dropna(), np.linspace(0, 1, 11))
                diffs = np.diff(q)
                cv = diffs.std() / diffs.mean()

                is_uniform = cv < 0.15

                col_profile["uniform_dist"] = is_uniform


                # Quantiles
                Q1 = series.quantile(0.25)
                median = series.quantile(0.5)
                Q3 = series.quantile(0.75)

                col_profile["Q1"] = float(Q1)
                col_profile["median"] = float(median)
                col_profile["range"] = float(series.max() - series.min())
                col_profile["IQR"] = float(Q3 - Q1)

                # Variance
                col_profile["variance"] = float(series.var())

                # Coefficient of variation (std / mean)
                col_profile["coefficient_of_variation"] = (
                    float(series.std() / series.mean()) if series.mean() != 0 else None
                )

                # MAD (Median Absolute Deviation)
                col_profile["MAD"] = float((series - median).abs().median())

                # Sum
                col_profile["sum"] = float(series.sum())

                # Monotonicity
                if series.is_monotonic_increasing:
                    col_profile["monotonicity"] = "increasing"
                elif series.is_monotonic_decreasing:
                    col_profile["monotonicity"] = "decreasing"
                else:
                    col_profile["monotonicity"] = "none"

                # Top 10 most common values
                value_counts = series.value_counts(dropna=False).head(10)
                total = len(series)

                top_values = []
                for val, count in value_counts.items():
                    top_values.append({
                        "value": None if pd.isna(val) else float(val),
                        "count": int(count),
                        "percent": float(count / total)
                    })

                col_profile["common_values"] = top_values

                # Top 10 maximum values
                max_values_counts = (
                    series.value_counts(dropna=False)
                          .sort_index(ascending=False)
                          .head(10)
                )
                total = len(series)

                max_values = []
                for val, count in max_values_counts.items():
                    max_values.append({
                        "value": None if pd.isna(val) else float(val),
                        "count": int(count),
                        "percent": float(count / total)
                    })

                col_profile["max_values"] = max_values


                # Top 10 minimum values
                min_values_counts = (
                    series.value_counts(dropna=False)
                          .sort_index(ascending=True)
                          .head(10)
                )

                min_values = []
                for val, count in min_values_counts.items():
                    min_values.append({
                        "value": None if pd.isna(val) else float(val),
                        "count": int(count),
                        "percent": float(count / total)
                    })

                col_profile["min_values"] = min_values


            if col_profile["type"] == "category":

                col_profile["top"] = series.mode().iloc[0] if not series.mode().empty else None
                col_profile["counts"] = series.value_counts().to_dict()
                col_profile["percentages"] = series.value_counts(normalize=True).to_dict()

                cats = series.unique()              # or series.cat.categories if categorical dtype
             
                # Convert all category names to strings
                cat_strs = [str(c) for c in cats]

                # Length of each category name
                lengths = [len(s) for s in cat_strs]

                # Total characters across all category names
                total_chars = sum(lengths)

                # Unique characters across all category names
                unique_chars = set("".join(cat_strs))
                total_unique_chars = len(unique_chars)

                stats = {
                    "min": int(np.min(lengths)),
                    "max": int(np.max(lengths)),
                    "mean": float(np.mean(lengths)),
                    "median": float(np.median(lengths)),
                    "total chars": int(total_chars),
                    "unique chars": int(total_unique_chars)
                }
                col_profile["cat_stats"] = stats


            if col_profile["type"] == "text":
                texts = series.unique()              # or series.cat.categories if categorical dtype
                text_strs = [str(c) for c in texts]
                lengths = [len(c) for c in text_strs]
                total_chars = sum(lengths)
                unique_chars = set("".join(text_strs))


                stats = {
                    "min": int(np.min(lengths)),
                    "max": int(np.max(lengths)),
                    "mean": float(np.mean(lengths)),
                    "median": float(np.median(lengths)),
                    "total chars": int(total_chars),
                    "unique chars": int(len(unique_chars))

                }

                col_profile["text_stats"] = stats
                # 1. Convert Series to a single string or iterate row-by-row
                texts = series.dropna().astype(str)

                # 2. Tokenize (simple whitespace split; replace with regex if needed)
                words = []
                for t in texts:
                    words.extend(t.lower().split())

                # 3. Count word frequencies
                counts = Counter(words)

                # 4. Compute percentages
                total = sum(counts.values())
                percentages = {w: counts[w] / total for w in counts}

                # 5. Extract top 10
                top10_counts = dict(counts.most_common(10))
                top10_percentages = {w: percentages[w] for w in top10_counts}
                col_profile["top words"] = top10_counts
                col_profile["top words percentages"] = top10_percentages
                
            
            columns[col] = col_profile

            

        return SectionResult(
            name=self.name,
            data=columns
        )
register_component(ColumnProfiler())
