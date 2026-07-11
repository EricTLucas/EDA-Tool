from loader import load_dataset
from profiler import Profiler
from visualizer import visualize_dataset
from html_report_generator import generate_html_report

def analyze(path_or_object, output_dir=r"reports"):
    df = load_dataset(path_or_object)
    print("Dataset Loading Complete")
    profile = Profiler(df)
    results = profile.run()
    print("Dataset Profiling Complete")
    visualize_dataset(df, results, output_dir)
    print("Dataset Visuals Complete")
    report_path = generate_html_report(df, profile, output_dir)
    print("HTML Report Generated")
    return df, profile