# ETML EDA

An automated Exploratory Data Analysis tool. Provide a dataset and generate a standalone HTML report with summary statistics, column analysis, missing values, visualizations, and data previews. Optional OpenAI analysis adds explanations, possible targets, and column dependencies.

## Install

Requires Python 3.10+. From the repository folder, use a separate environment from ETML Workbench:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[ui,library]"
```

On macOS/Linux, activate with `source .venv/bin/activate` instead.

## Start the UI

```bash
eda ui
```

Your browser opens automatically. Upload a dataset, enter a file path, or choose a library dataset, then click **Import & generate EDA**. View or download the HTML report.

## Quick CLI

```bash
eda iris.csv
eda "path/to/data-folder"
eda iris.csv -o reports/iris --noai
```

The report opens automatically. Runs are saved under `eda-output/` unless you choose a new output directory with `-o`.

- `--name "Dataset name"`: set the report title.
- `--noai`: disable AI analysis.
- `--no-open`: save without opening the browser.
- `eda analyze --help`: show all analysis options.

## OpenAI API key (optional)

In the UI, open **OpenAI API key** in the sidebar, enter your key, and enable AI analysis. The key stays in server memory until restart; it is never saved in datasets or reports. The key box opens when a key is missing or rejected.

Alternatively, set the environment variable before starting the UI or CLI:

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key"
```

```bash
# macOS/Linux
export OPENAI_API_KEY="your-api-key"
```

The quick CLI uses AI automatically when this variable is set; use `--noai` to disable it. AI sends column names, statistics, and any supplied explanation to OpenAI; sample values are optional. Local EDA works without a key.
