import profiler.summary
import profiler.column_profiler
from profiler import Profiler 
from loader import load_dataset
from visualizer import visualize_dataset

def main():

    #df = load_dataset("tests/sample_files/iris.csv") 
    df = load_dataset("tests/sample_files/000d7d20__horizontal_well.csv")
   
    profiler = Profiler(df)
    results = profiler.run()

    # Gives dict with Structure: 'name' : SectionResult(name, data = {})
    # access with report['component'].data['type']
    visualize_dataset(df, results, "reports")
    

if __name__ == "__main__":
    main()
