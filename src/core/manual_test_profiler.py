import profiler.summary
import profiler.column_profiler
from profiler import Profiler 
from loader import load_dataset

def main():

    df = load_dataset("tests/sample_files/iris.csv") 
    #df = load_dataset("tests/sample_files/000d7d20__horizontal_well.csv")
   
    profiler = Profiler(df)
    results = profiler.run()

    for name, section in results.items():
        print(f"\n=== {name.upper()} ===")
        print("DATA:")
        for k, v in section.data.items():
            print(f"  {k}: {v}")

        if section.warnings:
            print("WARNINGS:")
            for w in section.warnings:
                print(f"  - {w}")

if __name__ == "__main__":
    main()
