import numpy as np
import pandas as pd
from pathlib import Path
from io import BytesIO
import pyarrow.parquet as pq
import pyarrow.feather as feather
import pyarrow.orc as orc
import pyarrow.ipc as ipc
import json

def load_dataset(source) -> pd.DataFrame:
    """
    Load a dataset from various sources, returns DataFrame.
    For now list of DataFrames will be concatenated. List of dicts and lists are converted to DataFrame.
    """
    if isinstance(source, pd.DataFrame):
        return source

    elif isinstance(source, list):
        if all(hasattr(f, "filename") for f in source):
            return load_from_upload(source)

        elif all(isinstance(x, pd.DataFrame) for x in source):
            return pd.concat(source, ignore_index=True)

        elif all(isinstance(x, dict) for x in source):
            return pd.DataFrame(source)

        elif all(isinstance(x, (list, tuple)) for x in source):
            return pd.DataFrame(source)

        raise TypeError("List input must contain uploaded files, DataFrames, dicts, or lists")

    elif isinstance(source, (str, Path)):
        path = Path(source)
        
        if path.is_file():
            return load_from_path_file(path)
        if path.is_dir():
            return load_from_path_folder(path)
        raise ValueError(f"Invalid path: {source}")
    else: 
        raise TypeError(f"Input must be of type file, folder, DataFrame, or list, not {type(source)}")



def load_from_upload(files: list) -> pd.DataFrame:
    """
    Takes in a list of uploaded files, reads them into DataFrames, and concatenates them.
    Expects each item to be an upload-like object with a `filename` attribute and a `file`-like
    buffer (e.g. FastAPI/Flask UploadFile). Returns an empty DataFrame for an empty input list.
    """
    if not isinstance(files, list):
        raise TypeError("files must be a list of uploaded file objects")

    if len(files) == 0:
        return pd.DataFrame()

    dfs = []
    for f in files:
        if not hasattr(f, "filename"):
            raise TypeError("All items in files must have a 'filename' attribute (uploaded file objects)")

        try:
            df = convert_to_dataframe(f)
            dfs.append(df)
        except Exception as exc:
            name = getattr(f, "filename", "<unknown>")
            raise ValueError(f"Failed to load uploaded file '{name}': {exc}") from exc

    return pd.concat(dfs, ignore_index=True, sort=False)
    
def load_from_path_file(path: Path) -> pd.DataFrame:
    """
    Load a single file from a given path into a DataFrame. Converts if necessary.
    """
    return convert_to_dataframe(path)

def load_from_path_folder(folder: Path) -> pd.DataFrame:
    """
    Load all files from a given folder path into DataFrames, concatenates them.
    """
    files = []
    for file in folder.iterdir():
        if file.is_file():
            df = convert_to_dataframe(file)
            files.append(df)
    return pd.concat(files, ignore_index=True)
  

def convert_to_dataframe(file) -> pd.DataFrame:
    """
    Convert various fully compatible dataset file types into a pandas DataFrame.
    Supports:
        - CSV, TSV, TXT (delimited)
        - Excel: .xls, .xlsx, .xlsm, .xlsb
        - ODS
        - JSON, JSONL, NDJSON
        - Parquet
        - Feather
        - ORC
        - Arrow IPC
        - Stata (.dta)
        - SAS (.sas7bdat)
        - SPSS (.sav, .zsav)
        - Pickle (.pkl)
        - HDF5 (.h5, .hdf5)
    """

    # Accept both file paths and in-memory uploaded files
    if hasattr(file, "filename"):  # FastAPI/Flask UploadFile
        filename = file.filename
        ext = Path(filename).suffix.lower()
        data = file.file.read()
        stream = BytesIO(data)
    else:
        file = Path(file)
        filename = file.name
        ext = file.suffix.lower()
        stream = file  # path-like object

    # --- TEXT / DELIMITED FILES ---
    if ext in {".csv"}:
        return pd.read_csv(stream)

    if ext in {".tsv"}:
        return pd.read_csv(stream, sep="\t")

    if ext in {".txt", ".dat", ".tab"}:
        return pd.read_csv(stream, sep=None, engine="python")

    # --- EXCEL / SPREADSHEETS ---
    if ext in {".xls", ".xlsx", ".xlsm", ".xlsb"}:
        return pd.read_excel(stream)

    if ext == ".ods":
        return pd.read_excel(stream, engine="odf")

    # --- JSON / NDJSON ---
    if ext == ".json":
        # Try flat JSON first
        try:
            return pd.read_json(stream)
        except ValueError:
            # Nested JSON → normalize
            obj = json.load(stream)
            return pd.json_normalize(obj)

    if ext in {".jsonl", ".ndjson"}:
        return pd.read_json(stream, lines=True)

    # --- COLUMNAR FORMATS ---
    if ext == ".parquet":
        return pd.read_parquet(stream)

    if ext == ".feather":
        return feather.read_feather(stream)

    if ext == ".orc":
        table = orc.ORCFile(stream).read()
        return table.to_pandas()

    if ext == ".arrow":
        table = ipc.RecordBatchFileReader(stream).read_all()
        return table.to_pandas()

    # --- STATISTICAL FORMATS ---
    if ext == ".dta":  # Stata
        return pd.read_stata(stream)

    if ext == ".sas7bdat":  # SAS
        return pd.read_sas(stream)

    if ext in {".sav", ".zsav"}:  # SPSS
        return pd.read_spss(stream)

    # --- PICKLE ---
    if ext in {".pkl", ".pickle"}:
        return pd.read_pickle(stream)

    # --- HDF5 ---
    if ext in {".h5", ".hdf5"}:
        return pd.read_hdf(stream)

    raise ValueError(f"Unsupported dataset file type: {ext}")