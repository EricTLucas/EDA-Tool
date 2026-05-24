from src.core.loader import load_from_upload, load_dataset

def test_empty_upload():
	df = load_from_upload([])
	assert df.empty

def test_load_single_file():
    df_dict = load_dataset("tests/sample_files/sample.csv")
    assert "sample" in df_dict
    assert df_dict["sample"].shape[0] > 0


"""
add the following samples: 
sample_files/
    ├── sample.csv
    ├── sample.xlsx
    ├── sample.json
    ├── nested.json
    ├── sample.parquet
    ├── folder/
    │   ├── file1.csv
    │   └── file2.csv

"""