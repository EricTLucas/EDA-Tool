from .loader import load_dataset
from .profiler import Profiler
from .visualizer import visualize_dataset
from .html_report import generate_html
from pathlib import Path
import webbrowser
import os

def build_html_report(path_or_object, output_dir=r"/plots", open_html=True):
    df = load_dataset(path_or_object)
    print("Dataset Loading Complete")
    profile = Profiler(df)
    results = profile.run()
    print("Dataset Profiling Complete")
    visualize_dataset(df, results, output_dir)
    print("Dataset Visuals Complete")

    dataset_name = determine_dataset_name(path_or_object)

    html = generate_html(results, output_dir, dataset_name)
    print("HTML Report Generated")

    output_file = Path(output_dir) / "eda_report.html"
    output_file.write_text(html, encoding="utf-8")
    
    if open_html:
        url = "file://" + os.path.abspath("eda_report.html")
        webbrowser.open(url)
    
    return output_file

def determine_dataset_name(source):
   
    import pandas as pd
    if isinstance(source, pd.DataFrame):
        return "dataframe"

    if isinstance(source, list):

        if all(hasattr(f, "filename") for f in source):
            if len(source) == 1:
                return Path(source[0].filename).stem
            return "combined"
        
        if all(isinstance(x, pd.DataFrame) for x in source):
            return "combined"

        if all(isinstance(x, dict) for x in source):
            return "dict_list"

        if all(isinstance(x, (list, tuple)) for x in source):
            return "list"

        return "unknown_list"

    if isinstance(source, (str, Path)):
        path = Path(source)

        if path.is_file():
            return path.stem

        if path.is_dir():
            return path.name

        return "unknown_path"

    if hasattr(source, "filename"):
        return Path(source.filename).stem

    return "unknown"

