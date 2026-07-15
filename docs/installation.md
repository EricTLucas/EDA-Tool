# Installation

## Requirements

- Python 3.9+
- pip
- A virtual environment is recommended

## 1. Clone the repository

```bash
git clone https://github.com/EricTLucas/EDA-Automation-Tool.git
cd EDA-Automation-Tool
```

## 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

## 3. Install the package

```bash
pip install -e .
```

This installs the EDA tool along with all required dependencies defined in pyproject.toml.

## 4. Verify installation

```bash
eda --help
```

You should see the CLI usage message.

## 5. Generate a test report

```bash
eda tests/sample_files/iris.csv --out reports/
```

Open:
reports/iris_report.html
to view the generated EDA report.