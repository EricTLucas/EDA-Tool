# Exploratory Data Analysis Tool
*A lightweight, modular exploratory data analysis pipeline with automatic HTML report generation.*

---

## Features

- Automatic dataset loading (CSV or folder)
- Column profiling:
  - Numeric summaries
  - Categorical summaries
  - Memory usage
  - Missing value detection
- Visualizations:
  - Histograms
  - Bar charts
  - Interaction plots
  - Missingness matrix
- Full HTML report generation:
  - Variables section
  - Interactions section
  - Summary tables
  - Embedded graphs
- Command‑line interface (CLI):
  - One command to run the entire pipeline
  - Optional output directory
  - Optional auto‑open HTML report
- Modular architecture:
  - Loader → Profiler → Visualizer → HTML Generator → Pipeline
- Test suite included

---

## Installation

Clone the repository:

```bash
git clone https://github.com/EricTLucas/eda-tool
cd eda-tool
