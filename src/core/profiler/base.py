"""
Base classes and shared interfaces for the profiling system.
Defines the core Profiler abstraction and the component interface
used by all submodules.
"""

from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd


# ---------------------------------------------------------------------------
# Standardized return type for each profiling section
# ---------------------------------------------------------------------------

@dataclass
class SectionResult:
    """Container for the output of a profiling component."""
    name: str
    data: Dict[str, Any]
    warnings: Optional[List[str]] = None


# ---------------------------------------------------------------------------
# Component interface
# ---------------------------------------------------------------------------

class ProfilerComponent(ABC):
    """
    Base interface for all profiler components.
    Each component receives a DataFrame and returns a SectionResult.
    """

    name: str

    @abstractmethod
    def compute(self, df: pd.DataFrame) -> SectionResult:
       
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Component registry 
# ---------------------------------------------------------------------------

_COMPONENT_REGISTRY: Dict[str, ProfilerComponent] = {}


def register_component(component: ProfilerComponent) -> None:
    """Register a component so the main Profiler can auto-discover it."""
    _COMPONENT_REGISTRY[component.name] = component


def get_registered_components() -> Dict[str, ProfilerComponent]:
    """Return all registered components."""
    return _COMPONENT_REGISTRY


# ---------------------------------------------------------------------------
# Main Profiler abstraction
# ---------------------------------------------------------------------------

class BaseProfiler(ABC):
    """
    Abstract base class for all profilers.
    Concrete profilers should implement the `run()` method.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def run(self) -> Dict[str, SectionResult]:
        """
        Execute the profiling pipeline and return a dictionary
        mapping section names to SectionResult objects.
        """
        raise NotImplementedError

    def run_registered_components(self) -> Dict[str, SectionResult]:
        """
        Run all components registered via register_component().
        """
        results = {}
        for name, component in get_registered_components().items():
            results[name] = component.compute(self.df, results)
        return results
