# Chart Decision Tree — Edge Cases and Advanced Selection

## Table of Contents
1. [Decision Flowchart](#decision-flowchart)
2. [Sample Size Considerations](#sample-size)
3. [Audience-Aware Selection](#audience)
4. [Combining Charts Effectively](#combining)
5. [Statistical Visualization Patterns](#statistical)
6. [ML and AI Visualization](#ml-viz)

---

## Decision Flowchart {#decision-flowchart}

```
START: What question are you answering?
│
├─ "How much?" or "Which is bigger?" → COMPARISON
│   ├─ How many categories?
│   │   ├─ 2-5: Horizontal bar chart
│   │   ├─ 6-15: Bar chart (sorted by value, not alphabetically)
│   │   ├─ 15-30: Lollipop chart
│   │   └─ 30+: Consider aggregating or filtering. Too many bars = no insight.
│   ├─ Comparing across 2 dimensions?
│   │   ├─ Few groups: Grouped bar
│   │   └─ Many groups: Heatmap (treat categories as grid)
│   └─ Comparing to a benchmark?
│       └─ Bullet chart or bar with reference line
│
├─ "How is it spread?" → DISTRIBUTION
│   ├─ Single variable?
│   │   ├─ n < 30: Strip plot (show every point)
│   │   ├─ n 30-200: Histogram + rug plot
│   │   ├─ n 200-5000: Histogram or violin
│   │   └─ n > 5000: Density plot (KDE)
│   ├─ Comparing distributions?
│   │   ├─ 2-3 groups: Overlaid histograms (opacity=0.6)
│   │   ├─ 3-8 groups: Violin or box plots
│   │   └─ 8+ groups: Ridgeline plot or faceted histograms
│   └─ Two variables jointly?
│       ├─ n < 5000: Scatter plot
│       └─ n > 5000: 2D histogram / density heatmap
│
├─ "Is there a relationship?" → RELATIONSHIP
│   ├─ 2 continuous variables: Scatter plot
│   │   ├─ Want to show trend? Add trendline="ols" or "lowess"
│   │   ├─ Overplotted? Reduce opacity or use density heatmap
│   │   └─ Third variable? Map to color (categorical) or size (continuous)
│   ├─ 3-6 continuous variables: Scatter matrix (EDA) or parallel coordinates
│   ├─ Correlation overview: Heatmap of correlation matrix
│   └─ Categorical relationships: Parallel categories or Sankey
│
├─ "What's the breakdown?" → COMPOSITION
│   ├─ Single level?
│   │   ├─ 2-3 parts: Pie chart is acceptable
│   │   ├─ 4-7 parts: Stacked bar (horizontal, one bar)
│   │   └─ 7+ parts: Treemap
│   ├─ Hierarchical?
│   │   ├─ 2-3 levels: Sunburst (interactive) or treemap
│   │   └─ 4+ levels: Icicle chart
│   ├─ Over time?
│   │   ├─ Absolute values: Stacked area
│   │   └─ Proportions: 100% stacked area
│   └─ Additive/subtractive flow?
│       └─ Waterfall chart
│
└─ "What's changing?" → TREND / TIME
    ├─ How many series?
    │   ├─ 1-3: Line chart (clear and simple)
    │   ├─ 4-7: Line chart with muted colors, highlight the important ones
    │   └─ 7+: Small multiples (facet_row or facet_col)
    ├─ Want to show volume/magnitude?
    │   └─ Area chart (stacked if showing composition)
    ├─ Irregular time intervals?
    │   └─ Scatter with lines (markers show actual data points)
    └─ Financial data?
        └─ Candlestick or OHLC
```

---

## Sample Size Considerations {#sample-size}

The right chart changes with data volume:

| n (rows) | Scatter | Histogram | Box | Violin | Density heatmap |
|----------|---------|-----------|-----|--------|----------------|
| < 30 | Show every point with jitter | Too few for bins | Unreliable quartiles | Not enough data | No |
| 30-200 | Good | Good (10-20 bins) | Good | Acceptable | No |
| 200-5000 | Good (may need opacity) | Good | Good | Excellent | Good |
| 5000-50K | Use WebGL (`render_mode="webgl"`) | Good | Good | Good | Preferred over scatter |
| 50K+ | Aggregate first or density heatmap | Good (auto-bin) | Good | Good | Required |

For large datasets, always use `px.scatter(..., render_mode="webgl")` or switch to `go.Scattergl` to avoid browser performance issues.

---

## Audience-Aware Selection {#audience}

| Audience | Prefer | Avoid | Notes |
|----------|--------|-------|-------|
| Executives | Bar, line, KPI cards, waterfall | Violin, parallel coords, scatter matrix | They want the answer, not the exploration |
| Data scientists | Violin, scatter matrix, faceted plots | Pie charts, 3D bars | They appreciate statistical rigor |
| General public | Bar, line, simple scatter, maps | Box plots, heatmaps, ECDF | Familiarity > precision |
| Analysts | Heatmaps, faceted plots, histograms | Overly simplified charts | They want to explore and drill down |

---

## Combining Charts Effectively {#combining}

### Subplot patterns with `make_subplots`

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Distribution", "Trend", "Comparison", "Relationship"),
    specs=[[{"type": "xy"}, {"type": "xy"}],
           [{"type": "xy"}, {"type": "xy"}]]
)

fig.add_trace(go.Histogram(x=df["value"], name="Distribution"), row=1, col=1)
fig.add_trace(go.Scatter(x=df["date"], y=df["value"], name="Trend"), row=1, col=2)
fig.add_trace(go.Bar(x=df["cat"], y=df["val"], name="By Category"), row=2, col=1)
fig.add_trace(go.Scatter(x=df["x"], y=df["y"], mode="markers", name="Scatter"), row=2, col=2)

fig.update_layout(height=800, showlegend=False, template="plotly_white")
```

### Marginal distributions

```python
# Scatter with marginal histograms — shows relationship AND individual distributions
fig = px.scatter(df, x="x", y="y", marginal_x="histogram", marginal_y="box")
```

This is one of the most underused features in Plotly. It packs three charts into one view.

---

## Statistical Visualization Patterns {#statistical}

### Confidence intervals

```python
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=dates, y=upper, mode="lines", line=dict(width=0), showlegend=False
))
fig.add_trace(go.Scatter(
    x=dates, y=lower, mode="lines", line=dict(width=0),
    fill="tonexty", fillcolor="rgba(68,68,68,0.2)", showlegend=False
))
fig.add_trace(go.Scatter(
    x=dates, y=mean, mode="lines", line=dict(color="rgb(31,119,180)"), name="Mean"
))
```

### A/B test results

```python
fig = px.bar(results, x="variant", y="conversion_rate", error_y="ci_95",
             color="variant", text="conversion_rate")
fig.update_traces(texttemplate="%{text:.2%}", textposition="outside")
```

### QQ plot (normality check)

```python
from scipy import stats
theoretical = stats.norm.ppf(np.linspace(0.01, 0.99, len(data)))
fig = px.scatter(x=theoretical, y=np.sort(data), labels={"x": "Theoretical", "y": "Sample"})
fig.add_trace(go.Scatter(x=[-3,3], y=[-3,3], mode="lines", name="Normal"))
```

---

## ML and AI Visualization {#ml-viz}

### Confusion matrix

```python
fig = px.imshow(confusion_matrix, text_auto=True,
                labels=dict(x="Predicted", y="Actual", color="Count"),
                color_continuous_scale="Blues")
```

### Feature importance

```python
importance_df = importance_df.sort_values("importance")
fig = px.bar(importance_df, x="importance", y="feature", orientation="h")
```

Always sort by value, not alphabetically. The ranking IS the insight.

### ROC curve

```python
fig = px.area(x=fpr, y=tpr, labels=dict(x="FPR", y="TPR"),
              title=f"ROC Curve (AUC={auc:.3f})")
fig.add_shape(type="line", x0=0, x1=1, y0=0, y1=1, line=dict(dash="dash"))
```

### PCA / t-SNE / UMAP

```python
fig = px.scatter(embeddings, x="dim1", y="dim2", color="label",
                 hover_data=["original_text"],
                 title="Document Embeddings (UMAP)")
```

For cluster visualization, always include hover data so users can inspect individual points. The story is in the outliers.
