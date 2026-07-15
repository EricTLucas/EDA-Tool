from eda_tool.loader import load_dataset
import pandas as pd

def test_load_single_csv():
    df = load_dataset("tests/sample_files/sample.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 3)

def test_load_single_excel():
    df = load_dataset("tests/sample_files/sample.xlsx")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 3)

def test_load_dataframe_input():
    df_in = pd.DataFrame({"a": [1, 2]})
    df_out = load_dataset(df_in)
    assert isinstance(df_out, pd.DataFrame)
    assert df_out.equals(df_in)

def test_load_list_of_dicts():
    data = [{"a": 1}, {"a": 2}]
    df = load_dataset(data)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 1)

def test_load_list_of_lists():
    data = [[1, 2], [3, 4]]
    df = load_dataset(data)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)

def test_load_folder_auto_merge():
    df = load_dataset("tests/sample_files/folder")
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 6

from io import BytesIO

class FakeUpload:
    def __init__(self, filename, data):
        self.filename = filename
        self.file = BytesIO(data)

def test_load_uploaded_file():
    upload = FakeUpload("sample.csv", b"a,b\n1,2\n3,4")
    df = load_dataset([upload])
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)