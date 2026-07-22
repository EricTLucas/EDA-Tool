from .pipeline import build_html_report
import argparse

def main():
    parser = argparse.ArgumentParser(description="EDA Tool")
    parser.add_argument("input", help="Path to dataset or folder")
    parser.add_argument("--out", help="Directory to save plots", default="/plots")
    parser.add_argument("--no-open", action="store_true", help="Do not automatically open the HTML report")

    args = parser.parse_args()
    build_html_report(args.input, args.out, open_html=not args.no_open)

if __name__ == "__main__":
    main()
