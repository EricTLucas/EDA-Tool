# Developer Guide

This guide explains how the project is structured and how to extend it.

## Folder Structure

src/eda_tool/
cli.py
generator.py
pipeline.py
loader.py
visualizer.py
profiler
html_report

## Key Modules

### `cli.py`
Handles command-line parsing and dispatch.

### `loader.py`
Converts csv and other file types to pandas DataFrame.

###	`profiler`
Class that creates dictionary profile summarizing important statistics of a DataFrame.

### `visualizer.py`
Creates graphs corresponding to profile.

### `generator.py`
Main orchestrator that builds the full HTML report.

### `pipeline.py`
Links loader, profiler, visualizer, and generator.

## Running Tests

```bash
pytest
```