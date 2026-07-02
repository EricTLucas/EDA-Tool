from .base import ProfilerComponent, SectionResult, register_component

class SummaryComponent(ProfilerComponent):
    name = "summary"

    def compute(self, df, profile):
        # Compute dataset-level summary
        summary = {}

        summary["rows"] = df.shape[0]
        summary["cols"] = df.shape[1]

        summary["num_duplicates"] = int(df.duplicated().sum())
        summary["memory_usage"] = int(df.memory_usage(deep=True).sum())
        summary["num_missing_cells"] = int(df.isna().sum().sum())

        return SectionResult(
            name=self.name,
            data=summary
            )

register_component(SummaryComponent())