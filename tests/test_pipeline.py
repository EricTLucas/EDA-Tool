from src.core.pipeline import analyze
import pandas as pd

def test_pipeline_runs(tmp_path="reports"):
    df, profile = analyze("tests/sample_files/customers-1000.csv", output_dir=tmp_path)
    assert isinstance(df, pd.DataFrame)
    assert isinstance(profile, dict)
    #assert len(list(tmp_path.iterdir())) > 0