# Command Line Interface (CLI)

The CLI provides a simple way to generate EDA reports.

## Usage

bash
eda <input_file> [options]

## Arguments

input_file : path to a csv file

## Options

--out <dir> : output directory for the report, defaults is reports
--no-open : Do not automatically open the HTML report

## Examples

eda iris.csv --out /output --no-open