from pipeline import analyze
import argparse

def main():
    parser = argparse.ArgumentParser(description="EDA Tool")
    parser.add_argument("input", help="Path to dataset or folder")
    parser.add_argument("--out", help="Directory to save plots", default=None)
    args = parser.parse_args()

    analyze(args.input, args.out)

if __name__ == "__main__":
    main()