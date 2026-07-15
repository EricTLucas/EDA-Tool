# Report Structure

The generated HTML report contains several sections:

## Header

- Dataset name
- Section Links

## Summary 

- Common statistics
- Alerts for each column

## Variables

- Detailed Statistics for each column
- Accompanying Graphs, either histogram or bar graph

## Interactions

- Scatterplot of every numeric column against each other

## Correlations

- Heatmap and correlation matrix

## Missing (if necessary)

- Graph of nonmissing values per column
- Matrix of where missing values are per index per column

## Samples 

- First and last 10 observations

## Layout

The report uses:

- `.section-box` for major sections  
- `.table-wrapper` for tables  
- `.details-panel` for expandable content  
- `.tabs` and `.inner-tabs` for navigation  