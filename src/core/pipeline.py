from loader import load_dataset
from profiler import profile_dataset
from visualizer import visualize_dataset

def analyze(path_or_object, output_dir=r"reports"):
    df = load_dataset(path_or_object)
    profile = profile_dataset(df)
    visualize_dataset(df, profile, output_dir)
    return df, profile

def main():
    _, _ = analyze(r"tests\sample_files\iris.csv")

if __name__ == "__main__":
    main()