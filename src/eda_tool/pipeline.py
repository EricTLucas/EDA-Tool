from .loader import load_dataset
from .profiler import Profiler
from .visualizer import visualize_dataset
from .html_report import build_html_report
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
    html = build_html_report(results, output_dir, path_or_object)
    print("HTML Report Generated")

    with open("eda_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    if open_html:
        url = "file://" + os.path.abspath("eda_report.html")
        webbrowser.open(url)

    return df, profile