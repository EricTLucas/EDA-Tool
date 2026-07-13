from .base import ProfilerComponent, SectionResult, register_component

class SummaryComponent(ProfilerComponent):
    name = "summary"

    def compute(self, df, profile):
        # Compute dataset-level summary
        summary = {}

        summary["rows"] = df.shape[0]
        summary["cols"] = df.shape[1]

        summary["num_duplicates"] = int(df.duplicated().sum())
        summary["percent_duplicates"] = summary["num_duplicates"] / summary["rows"] if summary["rows"] > 0 else 0
        summary["memory_usage"] = int(df.memory_usage(deep=True).sum())
        summary["num_missing_cells"] = int(df.isna().sum().sum())
        summary["percent_missing_cells"] = summary["num_missing_cells"] / (summary["rows"] * summary["cols"]) if summary["rows"] > 0 and summary["cols"] > 0 else 0
        summary["sample_values_first"] = df.head(10)
        summary["sample_values_last"] = df.tail(10)
        summary["total_memory_usage"] = int(df.memory_usage(deep=True).sum())


        return SectionResult(
            name=self.name,
            data=summary
            )

register_component(SummaryComponent())