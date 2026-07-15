from eda_tool.profiler import profile_dataset

import pandas as pd

def test_profiler_basic():
    df = pd.DataFrame({"a":[1,2,3], "b":["x","y","z"]})
    profile = profile_dataset(df)
    assert isinstance(profile, dict)

def test_profiler_columns():
    df = pd.DataFrame({"a":[1,2,3]})
    profile = profile_dataset(df)
    assert "a" in profile["columns"]
    assert profile["columns"]["a"]["num_unique"] == 3

def test_numeric_stats():
    df = pd.DataFrame({"a":[1,2,3]})
    profile = profile_dataset(df)
    assert profile["columns"]["a"]["mean"] == 2

def test_missing_warning():
    df = pd.DataFrame({"a":[1,None,None]})
    profile = profile_dataset(df)
    assert any("50% missing" in w for w in profile["warnings"])