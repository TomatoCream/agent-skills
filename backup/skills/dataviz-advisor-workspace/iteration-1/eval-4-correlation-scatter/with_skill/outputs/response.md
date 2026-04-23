# Recommendation: Scatter Plot with OLS Trendline

## The Question You're Answering

This is a **relationship** question: "How are these two continuous variables connected?" The decision framework maps directly: **2 continuous variables + n ~ 200 = scatter plot with trendline**.

## Why a Scatter Plot

Scatter plots encode both variables as **position on a common scale**, which sits at the very top of Cleveland & McGill's perceptual hierarchy (1984). Position is the most accurate visual channel humans have -- subjects decode it with roughly 1-2% error. No other chart type gives you this level of precision for two continuous variables simultaneously.

With a scatter plot you can see:
- **Direction** of the relationship (positive, negative, or none)
- **Strength** of the correlation (tight cloud vs diffuse spread)
- **Linearity** -- whether the relationship is linear or curved
- **Outliers** -- individual points that deviate from the pattern
- **Clusters** -- subgroups that may follow different patterns

These are all visible at a glance because the human visual system detects structure in point clouds pre-attentively.

## Why Add a Trendline

A bare scatter plot shows the relationship; an OLS trendline quantifies it. Use `trendline="ols"` to overlay a linear regression line. For a technical audience, display the R-squared value and regression equation so the viewer can assess both the direction and the strength of the linear association numerically.

If the scatter suggests a non-linear pattern (curvature in the point cloud), switch to `trendline="lowess"` for a locally-weighted fit that follows the shape of the data without imposing linearity.

## Sample Size Considerations

At n = 200, you are in the sweet spot for a standard scatter plot. The sample size table confirms:
- **30-500**: Default scatter works perfectly -- enough points to reveal structure, few enough to avoid overplotting
- No need for opacity reduction (that kicks in around 500+)
- No need for WebGL rendering (that's for 5K+)
- No need for density heatmaps (that's for 50K+)

You can optionally add marginal distributions (`marginal_x="histogram"`, `marginal_y="box"`) to simultaneously show each variable's individual distribution alongside the joint relationship. This is an effective combination that reveals both the relationship and the univariate shapes in a single view.

## Why Not Other Charts

| Alternative | Why Not |
|---|---|
| **Heatmap (correlation matrix)** | Useful when you have many variables and want to scan all pairwise correlations at once. With only 2 variables, a correlation matrix is a single cell -- it tells you the r value but loses all the detail about shape, outliers, and non-linearity. |
| **Line chart** | Lines imply continuity and temporal ordering. Unless one of your variables is time and the data is sequential, a line chart would falsely suggest an ordering that does not exist. |
| **Paired bar chart** | Bars encode length, which is lower in the perceptual hierarchy than position. Bars also discretize continuous data, destroying the very relationship you are trying to see. |
| **Parallel coordinates** | Designed for high-dimensional data (7+ variables). For 2 variables it adds complexity without benefit. |

## Implementation

```python
import plotly.express as px

fig = px.scatter(
    df,
    x="variable_a",
    y="variable_b",
    trendline="ols",
    title="Relationship Between Variable A and Variable B",
    labels={"variable_a": "Variable A", "variable_b": "Variable B"},
)
fig.update_layout(template="plotly_white")
fig.show()

# Print regression statistics (R-squared, coefficients, p-value)
results = px.get_trendline_results(fig)
print(results.iloc[0]["px_fit_results"].summary())
```

### Enhanced version with marginal distributions

```python
fig = px.scatter(
    df,
    x="variable_a",
    y="variable_b",
    trendline="ols",
    marginal_x="histogram",
    marginal_y="histogram",
    title="Correlation Analysis (n=200)",
    labels={"variable_a": "Variable A", "variable_b": "Variable B"},
)
fig.update_layout(template="plotly_white")
fig.show()
```

### If you suspect non-linearity

```python
fig = px.scatter(
    df,
    x="variable_a",
    y="variable_b",
    trendline="lowess",
    title="Relationship with LOWESS Smooth",
    labels={"variable_a": "Variable A", "variable_b": "Variable B"},
)
fig.update_layout(template="plotly_white")
fig.show()
```

## Anti-Patterns to Avoid

1. **Do not use a line chart** unless one variable is ordered/temporal. Lines imply continuity between adjacent points, which misleads when no ordering exists.
2. **Do not truncate axes arbitrarily** -- let Plotly auto-range so the viewer sees the full spread of the data. For scatter plots (position encoding), zooming is acceptable, but make sure you are not hiding relevant outliers.
3. **Do not add a 3rd encoding (color/size) unless you have a 3rd variable** to map. Gratuitous visual complexity reduces the signal-to-noise ratio.
4. **Do not force a linear trendline if the relationship is clearly curved** -- use LOWESS instead, or consider transforming one of the variables (e.g., log scale).

## Setup

If you have not set up your environment yet:

```bash
uv init --app
uv add plotly pandas numpy scipy kaleido
```

The `scipy` package is included because Plotly uses it internally for OLS trendline calculations and you may want it for additional statistical tests (e.g., `scipy.stats.pearsonr` for the correlation coefficient and p-value).
