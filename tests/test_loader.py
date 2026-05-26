from src.core.loader import load_from_upload, load_dataset
from io import BytesIO

def test_empty_upload():
	df = load_from_upload([])
	assert df.empty

def test_load_single_file():
    df_dict = load_dataset("tests/sample_files/sample.csv")
    assert "sample" in df_dict
    assert df_dict["sample"].shape[0] > 0

def test_load_folder():
    df_dict = load_dataset("tests/sample_files/folder")
    assert len(df_dict) == 2

def test_load_dataframe():
    import pandas as pd
    df = pd.DataFrame({"a": [1,2]})
    result = load_dataset(df)
    assert "dataset" in result

def test_load_list_of_dataframes():
    import pandas as pd
    df_list = [pd.DataFrame({"a":[1]}), pd.DataFrame({"b":[2]})]
    result = load_dataset(df_list)
    assert len(result) == 2

def test_load_list_of_dicts():
    data = [{"a":1}, {"a":2}]
    result = load_dataset(data)
    assert "dataset" in result

class FakeUpload:
    def __init__(self, filename, data):
        self.filename = filename
        self.file = BytesIO(data)

def test_load_upload_files():
    files = [FakeUpload("sample.csv", b"a,b\n1,2")]
    result = load_dataset(files)
    assert "sample" in result