# Chart Decision Tree — Extended Reference

## Table of Contents
1. [Decision Flowchart by Question Type](#decision-flowchart-by-question-type)
2. [Edge Cases and Tricky Decisions](#edge-cases-and-tricky-decisions)
3. [Sample Size Deep Dive](#sample-size-deep-dive)
4. [Audience-Aware Selection](#audience-aware-selection)
5. [Combining Charts](#combining-charts)
6. [Statistical Visualization Patterns](#statistical-visualization-patterns)
7. [ML and AI Visualization Patterns](#ml-and-ai-visualization-patterns)

---

## Decision Flowchart by Question Type

### COMPARISON

```
How many categories?
├── 1-5 categories
│   ├── With subcategories? → Grouped bar
│   ├── Actual vs target? → Bullet chart
│   └── Simple comparison → Horizontal bar (sorted by value)
├── 6-15 categories
│   ├── All values similar magnitude? → Lollipop (less ink)
│   └── Wide range of values? → Horizontal bar (sorted)
├── 16+ categories
│   ├── Can you aggregate? → Top N + "Other" bar
│   └── Must show all → Faceted small multiples or heatmap
└── Multi-dimensional profile (5-10 dims)?
    └── Radar/spider (use sparingly — area encoding is imprecise)
```

**Sorting rule**: Almost always sort bars by value, not alphabetically. The ranking is part of the insight. Only sort alphabetically when the category order is inherently meaningful (months, rating scales).

**Horizontal vs vertical**: Use horizontal bars when category labels are long (>8 chars). Humans read left-to-right labels faster than rotated vertical labels.

### DISTRIBUTION

```
How many distributions?
├── 1 distribution
│   ├── n < 30 → Strip/jitter plot (show every point)
│   ├── 30-200 → Histogram (10-20 bins, Freedman-Diaconis rule)
│   ├── 200-5K → Histogram or KDE
│   └── Need exact percentiles? → ECDF
├── 2-5 distributions to compare
│   ├── Is shape important (bimodality)? → Violin plot
│   ├── Just need summary stats? → Box plot
│   ├── n < 200 per group? → Strip + box overlay
│   └── Want overlay comparison? → ECDF (overlay two = visual KS test)
├── 6-20 distributions
│   ├── Ordered categories? → Ridgeline plot
│   └── Unordered? → Faceted histograms or box plots
└── Joint distribution (2 numeric vars)?
    ├── n < 5000 → Scatter with marginal histograms
    └── n >= 5000 → 2D density heatmap
```

**Bin count guidance**:
- Freedman-Diaconis: `bin_width = 2 * IQR * n^(-1/3)` — robust to outliers
- Sturges: `bins = 1 + log2(n)` — simple, works for normal-ish data
- Scott: `bin_width = 3.49 * std * n^(-1/3)` — assumes normality
- When in doubt, try multiple bin counts and pick the one that reveals structure without creating noise

### RELATIONSHIP

```
How many variables?
├── 2 continuous variables
│   ├── n < 5000 → Scatter + trendline="ols"
│   ├── n 5K-50K → Scatter with WebGL + opacity
│   ├── n > 50K → 2D density heatmap or hexbin
│   └── Want to see marginals? → px.scatter with marginal_x/marginal_y
├── 3 continuous variables
│   ├── 3rd as color → Scatter + color
│   └── 3rd as size → Bubble (but area perception is imprecise)
├── 4+ continuous variables
│   ├── 3-6 variables → Scatter matrix (px.scatter_matrix)
│   └── 7+ variables → Parallel coordinates
├── Correlation matrix (many vars)
│   └── Heatmap with diverging colorscale (RdBu) centered at 0
└── Categorical relationship
    └── Parallel categories (px.parallel_categories)
```

**Trendline guidance**: `trendline="ols"` adds a linear regression line. For nonlinear patterns, use `trendline="lowess"`. Always show the trendline equation and R² when the audience is technical.

### COMPOSITION

```
Is the data hierarchical?
├── No (flat categories)
│   ├── Static snapshot → Stacked bar or 100% stacked bar
│   ├── Few categories (2-3) → Pie (only acceptable case)
│   ├── Sequential dropoff → Funnel
│   └── Cumulative build/subtract → Waterfall
└── Yes (nested categories)
    ├── 2-3 levels → Sunburst (interactive drill-down)
    ├── 3+ levels → Icicle (linear layout, easier to read than deep sunburst)
    └── Size comparison matters most → Treemap
```

**100% stacked vs regular stacked**: Use 100% stacked when the absolute totals differ significantly across groups and you want to compare proportions. Use regular stacked when the total itself carries meaning.

### CHANGE OVER TIME

```
How many series?
├── 1 series
│   ├── Continuous trend → Line chart
│   ├── Discrete intervals (yearly, monthly) → Bar chart
│   └── Financial OHLC → Candlestick
├── 2-5 series
│   ├── Independent comparison → Multiple lines (different colors)
│   ├── Part-of-whole over time → Stacked area
│   └── Same metric, different segments → Faceted lines (small multiples)
├── 6+ series
│   ├── Can highlight key series? → Line with grey background + 2-3 highlighted
│   └── All series equally important → Faceted small multiples
└── Animated evolution?
    └── Animated scatter (Gapminder-style with animation_frame)
```

**Time axis rule**: Never use bars for continuous time data unless the intervals are truly discrete and non-adjacent. Lines convey continuity; bars suggest independence.

**Annotation**: Always annotate significant events (product launches, policy changes, incidents) on time series. Context transforms a wiggly line into a story.

### SPATIAL

```
What kind of spatial data?
├── Values by region (country, state, zip)
│   ├── Administrative boundaries → Choropleth
│   └── Beware: large regions dominate visually (Alaska vs Rhode Island)
├── Point locations
│   ├── n < 5000 → Scatter map
│   └── n > 5000 → Density map (heatmap layer)
├── Routes or connections
│   └── Line map
└── Flow between locations
    └── Sankey or arc map
```

---

## Edge Cases and Tricky Decisions

### "Should I use a pie chart?"
Only if ALL of these are true:
1. You have 2-3 slices
2. The audience expects a pie chart (non-technical stakeholders)
3. Rough proportions suffice (not precise comparison)
4. You're showing parts of a single whole

If any condition fails, use a bar chart.

### "My scatter plot is a blob of overplotted points"
Escalation ladder:
1. Add opacity: `opacity=0.3`
2. Add jitter (for discrete values)
3. Use WebGL: `render_mode="webgl"` (for 5K-50K points)
4. Switch to 2D density heatmap: `px.density_heatmap` (for 50K+)
5. Aggregate: bin into hexagons or squares

### "I have time + categories + values"
This is the most common real-world scenario. Options:
- **Line chart with color**: Each category is a separate line
- **Faceted lines**: One small multiple per category (cleaner when >5 categories)
- **Heatmap**: Categories on y-axis, time on x-axis, value as color (good for spotting patterns across many categories)
- **Stacked area**: When composition over time matters

### "Someone asked for a dual y-axis chart"
Push back. Dual y-axes are almost always confusing because:
- The scale relationship is arbitrary — you can make any correlation look strong or weak by adjusting scales
- Readers don't know which axis to reference for which line
- Instead: use faceted subplots (same x-axis, separate y-axes) or normalize both series to a common scale (z-scores, percent change from baseline)

### "My boss wants 3D"
Resist. 3D adds perspective distortion that makes comparison impossible. The only legitimate uses of 3D:
- 3D scatter for genuinely 3-dimensional spatial data (molecular structures, point clouds)
- Surface plots for mathematical functions
- Never for bar charts, never for pie charts

---

## Sample Size Deep Dive

### Scatter plots by n

| n | Technique | Plotly code |
|---|-----------|-------------|
| < 30 | Show every point, label them | `px.scatter(..., text="label", hover_name="id")` |
| 30-500 | Default scatter | `px.scatter(df, x="a", y="b")` |
| 500-5K | Reduce opacity | `px.scatter(..., opacity=0.4)` |
| 5K-50K | WebGL rendering | `px.scatter(..., render_mode="webgl", opacity=0.2)` |
| 50K-500K | 2D density | `px.density_heatmap(df, x="a", y="b", nbinsx=50, nbinsy=50)` |
| 500K+ | Sample or aggregate | Downsample to 50K, or aggregate into bins |

### Histogram bin counts by n

| n | Recommended bins | Rule |
|---|-----------------|------|
| < 30 | 5-7 | Manual selection |
| 30-100 | 7-15 | Sturges: `1 + log2(n)` |
| 100-1K | 15-30 | Freedman-Diaconis |
| 1K-10K | 30-50 | Freedman-Diaconis |
| 10K+ | 50-100 | Auto or Freedman-Diaconis |

### When to switch chart types entirely

- **Violin → Box**: When comparing >10 groups (violins get too narrow to read)
- **Scatter → Density heatmap**: When overplotting makes scatter unreadable (typically n > 5K)
- **Individual lines → Aggregated ribbon**: When >20 time series makes spaghetti (show mean + confidence band)
- **Bar → Dot/lollipop**: When >15 categories (less visual weight, easier to scan)

---

## Audience-Aware Selection

### Executive dashboards
- **Goal**: Answer "how are we doing?" in <5 seconds
- **Charts**: KPI cards (big numbers), bar charts, line charts, waterfall
- **Rules**: Max 4-6 charts per view. No more than 2 chart types. Title = the insight, not the metric name ("Revenue grew 12% QoQ" not "Quarterly Revenue")
- **Avoid**: Violin, parallel coordinates, scatter matrix, ECDF, anything requiring statistical literacy

### Data science exploration
- **Goal**: Find patterns, validate assumptions, debug models
- **Charts**: Violin, scatter matrix, ECDF, faceted plots, parallel coordinates, heatmaps
- **Rules**: Information density is good. Interactivity is essential. Show uncertainty.
- **Avoid**: Oversimplified charts that hide distribution shape

### Client/public presentations
- **Goal**: Communicate one clear message
- **Charts**: Bar, line, simple scatter, annotated maps
- **Rules**: One chart = one message. Annotate the key insight directly on the chart. Use consistent, branded colors.
- **Avoid**: Box plots, heatmaps, ECDF, anything that requires explanation

### Analyst self-serve dashboards
- **Goal**: Enable exploration without code
- **Charts**: Filterable bar, heatmap, faceted views, drill-down treemaps
- **Rules**: Add dropdowns, sliders, cross-filtering. Let them answer their own questions.
- **Consider**: Dash for custom dashboards, or Tableau/PowerBI for non-technical analysts

---

## Combining Charts

### Effective combinations
- **Scatter + marginal histograms**: Shows both the relationship and individual distributions (`marginal_x="histogram"`, `marginal_y="histogram"`)
- **Line + shaded confidence interval**: Shows trend and uncertainty
- **Bar + reference line**: Actual values vs target/average (`fig.add_hline()`)
- **Heatmap + dendrogram**: Clustered correlation matrix (reveals variable groupings)
- **Map + bar/line insets**: Geographic overview + detail for selected region

### Subplot patterns
```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Shared x-axis (time) with different y metrics
fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    subplot_titles=["Revenue", "Customer Count"])
```

### Dashboard layout principles
- **Z-pattern**: Most important chart top-left, summary KPIs across top
- **Inverted pyramid**: Overview first (line/bar), then detail (heatmap/scatter)
- **Consistent encoding**: Same color = same category everywhere in the dashboard
- **Linked interactions**: Clicking a bar in chart A filters chart B (requires Dash)

---

## Statistical Visualization Patterns

### Confidence intervals
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y_upper, mode='lines', line=dict(width=0), showlegend=False))
fig.add_trace(go.Scatter(x=x, y=y_lower, mode='lines', line=dict(width=0),
                         fill='tonexty', fillcolor='rgba(68,68,68,0.2)', showlegend=False))
fig.add_trace(go.Scatter(x=x, y=y_mean, mode='lines', name='Mean'))
```

### A/B test results
```python
fig = px.bar(results, x="variant", y="conversion_rate",
             error_y="confidence_interval", color="variant",
             title="Variant B: +2.3% conversion (p=0.003)")
```
Always include: effect size, confidence interval, p-value in the title or annotation.

### QQ plot (normality check)
```python
from scipy import stats
import numpy as np

theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(data)))
sample_quantiles = np.sort(data)

fig = px.scatter(x=theoretical_quantiles, y=sample_quantiles,
                 labels={"x": "Theoretical Quantiles", "y": "Sample Quantiles"})
fig.add_shape(type="line", x0=min(theoretical_quantiles), x1=max(theoretical_quantiles),
              y0=min(theoretical_quantiles), y1=max(theoretical_quantiles),
              line=dict(dash="dash", color="red"))
```

### Confusion matrix
```python
fig = px.imshow(confusion_matrix, text_auto=True,
                labels=dict(x="Predicted", y="Actual", color="Count"),
                color_continuous_scale="Blues",
                x=class_names, y=class_names)
```

### Feature importance
```python
importance_df = importance_df.sort_values("importance")  # Sort ascending for horizontal bar
fig = px.bar(importance_df, x="importance", y="feature", orientation="h",
             title="Feature Importance (Top 20)")
```
The horizontal sorted bar makes the ranking immediately visible — the position IS the insight.

### ROC curve
```python
fig = px.area(x=fpr, y=tpr, labels=dict(x="False Positive Rate", y="True Positive Rate"),
              title=f"ROC Curve (AUC = {auc:.3f})")
fig.add_shape(type="line", x0=0, x1=1, y0=0, y1=1,
              line=dict(dash="dash", color="grey"))
```

---

## ML and AI Visualization Patterns

### PCA / t-SNE / UMAP embeddings
```python
fig = px.scatter(embeddings_df, x="dim1", y="dim2", color="cluster",
                 hover_data=["original_text", "label"],
                 title="Document Embeddings (UMAP)")
```
The story is in the outliers and cluster boundaries. Always include hover data with the original features so users can investigate interesting points.

### Learning curves
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=train_sizes, y=train_scores, name="Training", mode="lines+markers"))
fig.add_trace(go.Scatter(x=train_sizes, y=val_scores, name="Validation", mode="lines+markers"))
# Gap between curves = overfitting. Convergence = good fit.
```

### Hyperparameter search
```python
fig = px.parallel_coordinates(results_df,
                               dimensions=["learning_rate", "n_estimators", "max_depth", "accuracy"],
                               color="accuracy", color_continuous_scale="Viridis")
```
Lines clustering toward high accuracy reveal the optimal parameter combinations.

### Residual plots
```python
fig = px.scatter(x=predicted, y=residuals, labels={"x": "Predicted", "y": "Residuals"})
fig.add_hline(y=0, line_dash="dash", line_color="red")
# Patterns in residuals = model is missing something. Random cloud = good fit.
```

### Class distribution / imbalance
```python
fig = px.bar(class_counts, x="class", y="count", color="class",
             title="Class Distribution (10:1 imbalance)")
fig.add_annotation(text="Consider SMOTE or class weights", x=0.5, y=0.95,
                   xref="paper", yref="paper", showarrow=False)
```
