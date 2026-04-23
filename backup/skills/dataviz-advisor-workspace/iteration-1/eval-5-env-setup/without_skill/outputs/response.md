# Data Analysis Project Setup - Complete

I set up a full data analysis environment within the existing `fp` project at `/Users/wongdingfeng/projects/fp`. Here is everything that was done.

## 1. Dependencies Added

Updated `/Users/wongdingfeng/projects/fp/pyproject.toml` with an `[project.optional-dependencies]` section called `analysis` containing:

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 3.0.1 | Data manipulation and analysis |
| numpy | 2.4.3 | Numerical computing |
| matplotlib | 3.10.8 | Static plotting |
| seaborn | 0.13.2 | Statistical visualizations |
| scipy | 1.17.1 | Scientific computing and statistical tests |
| scikit-learn | 1.8.0 | Machine learning |
| plotly | 6.6.0 | Interactive visualizations |
| jupyter | 1.1.1 | Notebook environment |
| notebook | 7.5.5 | Jupyter Notebook server |
| ipykernel | 7.2.0 | Python kernel for Jupyter |
| openpyxl | 3.1.5 | Excel file support |

Install with: `uv sync --extra analysis`

## 2. Directory Structure Created

```
fp/
├── data/
│   ├── raw/           # Place source data files here
│   ├── processed/     # Cleaned / transformed data
│   └── output/        # Figures, reports, final results
├── notebooks/
│   └── 01_exploratory_analysis.ipynb   # EDA starter notebook
└── src/
    └── analysis/
        ├── __init__.py
        ├── loader.py      # Data loading/saving utilities
        ├── stats.py       # Statistical analysis utilities
        └── visualize.py   # Visualization utilities
```

## 3. Analysis Modules

### `src/analysis/loader.py`
Convenience functions for loading and saving data in various formats:
- `load_csv()`, `load_excel()`, `load_json()` -- load from `data/raw/` (or any subdirectory)
- `save_csv()`, `save_excel()` -- save to `data/processed/` (or any subdirectory)
- Exports path constants: `RAW_DIR`, `PROCESSED_DIR`, `OUTPUT_DIR`

### `src/analysis/stats.py`
Statistical analysis utilities:
- `summary_stats(df)` -- extended descriptive statistics including median, skewness, kurtosis, and missing value counts
- `correlation_matrix(df, method)` -- correlation matrix with pearson/kendall/spearman support
- `detect_outliers_iqr(series, factor)` -- IQR-based outlier detection
- `normality_test(series)` -- Shapiro-Wilk normality test

### `src/analysis/visualize.py`
Visualization utilities built on matplotlib and seaborn:
- `distribution_plot(df, column, kind)` -- histogram, KDE, or box plot for a single column
- `correlation_heatmap(df, method)` -- annotated heatmap of correlations
- `scatter_matrix(df, columns, hue)` -- pair plot with optional color grouping
- `time_series_plot(df, date_column, value_columns)` -- multi-line time series plot

All plot functions accept `save=True` to write figures to `data/output/`.

## 4. Starter Notebook

`/Users/wongdingfeng/projects/fp/notebooks/01_exploratory_analysis.ipynb` is a ready-to-run EDA template covering:

1. Data loading (with a sample dataset for demonstration)
2. Data overview (types, missing values, duplicates)
3. Extended descriptive statistics
4. Distribution plots for all numeric columns
5. Correlation heatmap
6. Outlier detection
7. Category analysis

## 5. Jupyter Kernel

A Jupyter kernel named **"Python (fp)"** was registered, so notebooks can use this project's virtual environment directly.

## How to Get Started

```bash
# Start Jupyter
uv run jupyter notebook

# Or run analysis in a script
uv run python -c "
from analysis.loader import load_csv
from analysis.stats import summary_stats
df = load_csv('your_data.csv')
print(summary_stats(df))
"
```

All packages have been installed and verified working. The smoke tests for all analysis modules passed successfully.
