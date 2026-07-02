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
                if col1 == col2: continue
                pairs.append((col1, col2))
                sampled[(col1, col2)] = df[[col1, col2]].sample(500, replace=True)
                

        return SectionResult(
            name=self.name,
            data={
                "pairs": pairs,
                "sampled": sampled
            }
        )


register_component(InteractionsComponent())
