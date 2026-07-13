from .loader import load_dataset
from .profiler import Profiler
from .visualizer import visualize_dataset
from .html_report_generator import generate_eda_html
import webbrowser
import os

def analyze(path_or_object, output_dir=r"figures", open_html=True):
    df = load_dataset(path_or_object)
    print("Dataset Loading Complete")
    profile = Profiler(df)
    results = profile.run()
    print("Dataset Profiling Complete")
    visualize_dataset(df, results, output_dir)
    print("Dataset Visuals Complete")
    html = generate_eda_html(df, results, output_dir)
    print("HTML Report Generated")

    with open("eda_report.html", "w", encoding="utf-8") as f:
        f.write(html)

    if open_html:
        ("eda_report.html")

    return df, profile


def open_html(path):
    url = "file://" + os.path.abspath(path)
    webbrowser.open(url)