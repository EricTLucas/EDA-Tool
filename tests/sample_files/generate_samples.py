import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.feather as feather
import pyarrow.orc as orc
import pyarrow.ipc as ipc
from pathlib import Path
import json

def main():
    base = Path(__file__).parent

    df = pd.DataFrame({
        "Column_1": [1, 2, -3, 5, 10],
        "Column_2": ["x", "y", "z", "a", "i"],
        "Column_3": [0.1, 0.8, 0.3, 0.9, 0.2]
    })

    # CSV
    df.to_csv(base / "sample.csv", index=False)

    # TSV
    df.to_csv(base / "sample.tsv", sep="\t", index=False)

    # TXT (delimited)
    df.to_csv(base / "sample.txt", sep="|", index=False)

    # Excel
    df.to_excel(base / "sample.xlsx", index=False)

    # JSON
    df.to_json(base / "sample.json", orient="records")

    # JSONL / NDJSON
    with open(base / "sample.jsonl", "w") as f:
        for _, row in df.iterrows():
            f.write(json.dumps(row.to_dict()) + "\n")

    # Parquet
    df.to_parquet(base / "sample.parquet")

    # Feather
    feather.write_feather(df, base / "sample.feather")

    # ORC
    table = pa.Table.from_pandas(df)
    orc.write_table(table, base / "sample.orc")

    # Arrow IPC
    with ipc.new_file(base / "sample.arrow", table.schema) as writer:
        writer.write(table)

    # Stata
    df.to_stata(base / "sample.dta")

    # Pickle
    df.to_pickle(base / "sample.pkl")

    # HDF5
    df.to_hdf(base / "sample.h5", key="data", mode="w")

    # Folder with multiple CSVs
    folder = base / "folder"
    folder.mkdir(exist_ok=True)
    df.to_csv(folder / "file1.csv", index=False)
    df.to_csv(folder / "file2.csv", index=False)

    print("Sample files generated.")

if __name__ == "__main__":
    main()