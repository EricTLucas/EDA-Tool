# ETML EDA

A standalone exploratory data analysis tool with a dark Orchid interface, batch
profiling, optional AI interpretation, and portable HTML reports. This repository
contains only the EDA application: it does not require ETML Workbench or its
preprocessing, task, model, training, or prediction packages.

## Start here

Use Python 3.10 or newer and a **separate virtual environment** from Workbench.
Both applications use the `eda_tool` Python namespace, so do not install them into
the same environment.

From this repository's folder, on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[ui,library]"
eda ui
```

On macOS/Linux, activate with `source .venv/bin/activate` instead. The remaining
commands are the same. The UI opens at **http://127.0.0.1:8765**. Stop it with Ctrl+C.

1. Click **Add dataset**.
2. Upload or drag a file, enter a local path, or choose a library dataset.
3. Optionally explain what the dataset and columns represent.
4. Click **Import & generate EDA**.
5. View the embedded report and first 10 raw rows. Open the report in a new tab or
   download its standalone HTML file.
6. Adjust profiling settings or individual column roles and generate another report.
   Previous reports remain available in the saved-reports selector.

Try the included `examples/demo.csv`, or choose **Scikit-learn → iris**.

## What it does

- Profiles missing values, distinct values, distributions, numeric statistics,
  categorical frequencies, text characteristics, associations and quality flags.
- Processes CSV/TSV and Parquet in batches. Uses bounded samples/caps for expensive
  analysis and identifies approximation methods in report metadata.
- Automatically treats low-cardinality columns as categories; allows manual role
  overrides for numeric, category, text and date columns.
- Produces summary charts and supports additional requested charts through the CLI
  and Python API. Run `eda charts` for the actual catalog and accepted options.
- Exports a self-contained HTML report with dataset summary, summary statistics,
  quality findings, a tabbed column browser, column plots and statistics tabs,
  potential targets, relationships, dependency review, and first/middle/last row previews.
- Optionally asks OpenAI to explain the dataset/columns, suggest targets, and identify
  possible dependencies. Without AI, profiling and charts still work normally.
- Keeps imported raw data and multiple saved report runs in a local workspace.

This is an exploration app, not a preprocessing or model-training application.

## Dataset library and optional packages

```powershell
python -m pip install -e ".[ui,library,kaggle,huggingface,excel]"
```

| Extra | Adds |
| --- | --- |
| `ui` | Browser UI: FastAPI, Uvicorn and file uploads |
| `library` | Scikit-learn example datasets and OpenML |
| `kaggle` | Kaggle competition downloads through the CLI |
| `huggingface` | Tabular Hugging Face dataset imports |
| `excel` | Excel/ODS reader dependencies |
| `test` | HTTP client for UI tests |

The UI also supports direct HTTP(S) data-file URLs. Kaggle requires an authenticated
Kaggle CLI and acceptance of the competition rules. Enter a competition slug such as
`titanic` and a filename such as `train.csv`. Use `kaggle competitions files titanic`
to discover filenames. Import a single partition at a time; files are not combined
into train/test roles in this EDA application.

Library imports from sklearn/OpenML/Hugging Face default to a 200,000-row and 512 MiB
limit; they fail rather than silently truncate. Direct file imports use a byte limit.
Hugging Face supports scalar tabular columns, not nested media datasets. Downloads
require network access. Kaggle's external CLI checks download size after downloading;
its network transfer itself is not bounded by the import byte limit.

## Optional AI analysis

Set the key in the environment of the terminal that starts the UI:

```powershell
$env:OPENAI_API_KEY = "your-key"
$env:ETML_OPENAI_MODEL = "gpt-5-mini"
eda ui
```

`ETML_OPENAI_MODEL` is optional; the current code default is `gpt-5-mini`. Use a model
available to your API project that supports the structured-output request used here.
The integration is in `src/eda_tool/intelligence.py`; API use may incur charges.

AI runs only when explicitly selected. It sends column names, selected aggregate
statistics and your explanation. The separate sample checkbox adds up to three short
values per column. The current limit is 100 columns and 12,000 explanation characters.
Keys stay server-side and are not written to reports. Generated interpretations and
dependencies are hypotheses, not verified facts. If AI fails, the local report is
still saved and includes an explanation of the failure. No live API calls are needed
for tests.

## CLI

Prefer the UI for interactive exploration. The CLI supports reproducible runs and
custom plots. `etml-eda` is an equivalent command; `python -m eda_tool` also works.

```powershell
# Generate a new saved run, HTML report and summary charts; open it in your browser.
eda analyze examples/demo.csv --output reports/demo --html --open

# Batch settings and a manual column role.
eda analyze data.csv --output reports/run-2 --html --batch-size 50000 --sample-size 10000 --role Age=numeric

# Optional interpretation.
eda analyze data.csv --output reports/ai-run --html --ai --explanation "One row per customer; Renewed is a possible target."

# Discover charts and create a specific plot from the source data.
eda charts
eda plot examples/demo.csv --kind histogram --x age --output reports/age.png

# Explicitly save sampled rows for later row-based plots without reopening the source.
eda analyze examples/demo.csv --output reports/sampled --html --save-sample
eda plot --run reports/sampled --kind scatter --x age --y spend --output reports/scatter.png

# Re-export a saved report, preserving its AI context.
eda report --run reports/demo --output reports/demo-copy.html

# Download/import a library dataset as a preserved raw snapshot.
eda fetch sklearn iris
eda fetch kaggle titanic --file train.csv
eda fetch huggingface organization/dataset --split train
```

`eda fetch` prints the saved source path; pass it to `eda analyze` or select it from
the UI's saved dataset list. Default fetch storage matches the default UI workspace.
Output run directories and chart files must not already exist. Choose a new name for
each run. Use `eda analyze --help`, `eda plot --help`, `eda fetch --help`, or `eda ui --help`
for full options. `--json` is available on analyze/plot/report/charts.

UI launch options:

```powershell
eda ui --data-dir my-eda-data --port 8766 --max-upload-mb 1024 --no-open
```

The server binds to loopback only. It is intended for one local user, not public hosting.
It runs one analysis job at a time. CLI runs may be executed separately.

## Python API

```python
from eda_tool import run_eda
from eda_tool.profiler import ProfileConfig

result = run_eda(
    "examples/demo.csv",
    profile_config=ProfileConfig(batch_size=50_000, roles={"age": "numeric"}),
    generate_summary=True,
    export_html=True,
    output_dir="reports/python-run",
    title="Customer exploration",
)
try:
    print(result.profile["summary"].data)
    print(result.html_path)
finally:
    result.close()  # release chart figures
```

The Python API also accepts `chart_requests`, `visualizer_config`, `loader_options`,
`report_context`, `ai`, `ai_samples`, and `explanation`. Without `output_dir`, results
stay in memory. See `src/eda_tool/workflows/eda.py` for the complete signature.

## Storage and limits

```text
eda-data/
  datasets/<dataset-id>/
    dataset.json
    raw/<original-file>
  runs/<run-id>/
    manifest.json
    report.html
    ... profile and chart artifacts ...
```

The HTML is portable: its styles and PNG charts are embedded, with no JavaScript or
network dependency. It includes original row previews and dataset-derived values;
review it before sharing. `--save-sample` adds a separate random sample artifact.

Batching does not make every format or statistic out-of-core. CSV/TSV and Parquet have
batch readers; other formats can use in-memory fallbacks. A row batch is not a byte
limit, and individual wide/large rows may still use significant memory. Associations,
quantiles and charts may use bounded samples; distinct-frequency tracking has caps.
The standard HTML shows up to 50 column cards and bounded charts; all profile data
remains in the saved run. Use explicit CLI/Python plots for other columns. Exact
source-order row previews may require an additional pass.

Common input formats include CSV, TSV, Parquet, JSON/JSONL, Feather, ORC and Excel/ODS.
Some readers need their own optional dependencies. Pickle loading is disabled by
default because it can execute code.

## Repository structure

```text
src/eda_tool/
  loader.py             Dataset readers
  profiler/             Batch aggregation and analysis
  visualization/        Chart implementations
  visualizer.py         Public chart API
  html_report/          Portable report rendering and context
  intelligence.py       Optional OpenAI interpretation
  artifacts/            Saved-run serialization and integrity checks
  workflows/            run_eda orchestration
  datasets/             EDA-only storage and provider imports
  cli.py                Standalone command-line entry point
  ui.py                 Local UI server
  web_static/           Browser interface
examples/demo.csv
tests/
pyproject.toml
```

## Development and tests

```powershell
python -m pip install -e ".[ui,library,test]"
python -m unittest discover -s tests -v
python -m pip wheel . --no-deps -w dist
```

This extracted repository intentionally includes no Workbench runtime modules, user
data, credentials, virtual environment, build outputs, or Git history. Create a new
GitHub repository and commit these files. Select your preferred license before
publishing if you want to grant reuse rights.

### Dataset names and UI API key

Set **Dataset name** when importing data; uploaded/local files default to their filename. The display name appears in the saved dataset list and report without renaming the raw file. Library imports also accept a custom name. CLI imports support `eda fetch path data.csv --dataset-name "My dataset"`.

The sidebar **OpenAI API key** box accepts a key for the current server session. It remains in server memory only and must be entered again after restarting, unless `OPENAI_API_KEY` is configured. The box opens when no key is available or OpenAI rejects authentication. Keys are checked during AI analysis; quota/access errors are reported separately. After replacing a key, enable AI and generate another report. Local EDA works without a key.
