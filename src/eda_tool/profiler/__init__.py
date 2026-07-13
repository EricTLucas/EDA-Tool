from .base import BaseProfiler, SectionResult, get_registered_components

class Profiler(BaseProfiler):
    def __init__(self, df):
        super().__init__(df)

    def run(self):
        results = {}
        for name, component in get_registered_components().items():
            results[name] = component.compute(self.df, results)

        return results


from . import summary
from . import column_profiler
from . import interactions
from . import correlations
from . import warnings

__all__ = ["Profiler", "SectionResult"]
