from .base import ProfilerComponent, SectionResult, register_component

class InteractionsComponent(ProfilerComponent):
    name = "interactions"

    def compute(self, df, profile):


        all_cols = profile["columns"].data
        

        numeric_cols = []

        for col in all_cols:
            if all_cols[col]["type"] == "numeric":
                numeric_cols.append(col)


        pairs = []

        sampled = {}


        for col1 in numeric_cols:
            for col2 in numeric_cols:
           
                pairs.append((col1, col2))

                if col1 == col2:
                    # Build a 2-column DataFrame with UNIQUE column names
                    df_pair = df[[col1]].copy()
                    df_pair[f"{col1}__dup"] = df_pair[col1]

                    # Remove NaNs BEFORE sampling
                    df_pair = df_pair.dropna()

                    # Sample up to 500 rows (if fewer exist, take all)
                    n = min(500, len(df_pair))
                    df_pair = df_pair.sample(n, replace=False)

                    # Rename duplicate column back to col1
                    df_pair.rename(columns={f"{col1}__dup": col2}, inplace=True)

                    sampled[(col1, col2)] = df_pair

                else:
                    # Normal pair
                    df_pair = df[[col1, col2]].dropna()

                    n = min(500, len(df_pair))
                    df_pair = df_pair.sample(n, replace=False)

                    sampled[(col1, col2)] = df_pair

        return SectionResult(
            name=self.name,
            data={
                "pairs": pairs,
                "sampled": sampled
            }
        )


register_component(InteractionsComponent())
