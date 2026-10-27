"""Standalone ETML EDA."""
__version__ = '1.0.1'

def run_eda(*args, **kwargs):
    from .workflows import run_eda as run
    return run(*args, **kwargs)
