import profiler.summary
import profiler.column_profiler
from profiler import Profiler 
from loader import load_dataset
from visualizer import visualize_dataset
from html_report_generator import generate_eda_html

def main():

    #df = load_dataset("tests/sample_files/iris.csv") 
    df = load_dataset("tests/sample_files/000d7d20__horizontal_well.csv")
   
    profiler = Profiler(df)
    results = profiler.run()

    # Gives dict with Structure: 'name' : SectionResult(name, data = {})
    # access with report['component'].data['type']

    #visualize_dataset(df, results, "reports")
    html = generate_eda_html(df, results, "reports")

    with open("eda_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    

if __name__ == "__main__":
    main()
