# Python API

The EDA tool can be used directly from Python.

## Main Function

```python
from eda_tool import build_html_report
build_html_report(input_path, output_dir)

input_path : Path to CSV file
output_dir : Directory where report is written

# Returns
A string containing the full HTML content.

## Example
```python
from eda_tool import build_html_report
html = build_html_report("iris.csv", "reports/")
with open("reports/iris.html", "w") as f:
    f.write(html)