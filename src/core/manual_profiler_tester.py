from profiler import profile_dataset
from loader import load_dataset
import pandas as pd

def main():
    
    # Sample dataset
    
    df = load_dataset("tests/sample_files/iris.csv")
    # Profile the dataset
    profile = profile_dataset(df)
    print(profile["columns"]["species"])


if __name__ == "__main__":
    main()