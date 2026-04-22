# Plotly Recipes — Implementation Cookbook

## Table of Contents
1. [Setup and Imports](#setup-and-imports)
2. [Comparison Charts](#comparison-charts)
3. [Distribution Charts](#distribution-charts)
4. [Relationship Charts](#relationship-charts)
5. [Composition Charts](#composition-charts)
6. [Time Series Charts](#time-series-charts)
7. [Spatial Charts](#spatial-charts)
8. [Statistical Patterns](#statistical-patterns)
9. [The Bridge Pattern: Express → Graph Objects](#the-bridge-pattern)
10. [Layout and Styling](#layout-and-styling)
11. [Export](#export)

---

## Setup and Imports

```python
# Express — use for 90% of charts
import plotly.express as px

# Graph Objects — use for complex/custom charts
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Data
import pandas as pd
import numpy as np
```

---

## Comparison Charts

### Horizontal sorted bar (the default for comparison)
```python
df = df.sort_values("value")  # Sort ascending — largest at top
fig = px.bar(df, x="value", y="category", orientation="h",
             title="Sales by Category",
             text="value", text_auto=".2s")
fig.update_layout(yaxis_title=None, template="plotly_white")
fig.show()
```

### Grouped bar (subcategory comparison)
```python
fig = px.bar(df, x="category", y="value", color="subcategory",
             barmode="group", title="Sales by Category and Region")
fig.update_layout(template="plotly_white")
```

### Lollipop (many categories, less ink)
```python
fig = go.Figure()
for _, row in df.iterrows():
    fig.add_trace(go.Scatter(x=[0, row["value"]], y=[row["category"], row["category"]],
                             mode="lines", line=dict(color="grey", width=1), showlegend=False))
fig.add_trace(go.Scatter(x=df["value"], y=df["category"],
                         mode="markers", marker=dict(size=10, color="#636EFA")))
fig.update_layout(template="plotly_white", showlegend=False)
```

### Bullet chart (actual vs target)
```python
fig = go.Figure()
# Background range
fig.add_trace(go.Bar(x=[target * 1.2], y=["Metric"], orientation="h",
                     marker_color="lightgrey", width=0.5))
# Target line
fig.add_trace(go.Scatter(x=[target], y=["Metric"], mode="markers",
                         marker=dict(symbol="line-ns", size=20, color="black", line_width=3)))
# Actual bar
fig.add_trace(go.Bar(x=[actual], y=["Metric"], orientation="h",
                     marker_color="#636EFA", width=0.25))
fig.update_layout(barmode="overlay", showlegend=False, template="plotly_white")
```

---

## Distribution Charts

### Histogram with bin count control
```python
fig = px.histogram(df, x="value", nbins=30, marginal="rug",
                   title="Distribution of Response Times",
                   labels={"value": "Response Time (ms)"})
fig.update_layout(template="plotly_white")
```

### Violin plot (reveals bimodality)
```python
fig = px.violin(df, x="group", y="value", box=True, points="outliers",
                title="Response Time by Endpoint",
                color="group")
fig.update_layout(template="plotly_white", showlegend=False)
```

### Box plot (compact, many groups)
```python
fig = px.box(df, x="group", y="value", color="group",
             notched=True,  # Shows confidence interval for median
             title="Distribution Comparison")
fig.update_layout(template="plotly_white", showlegend=False)
```

### Strip/jitter (small n, show every point)
```python
fig = px.strip(df, x="group", y="value", color="group",
               title="Individual Measurements (n=50 per group)")
fig.update_layout(template="plotly_white")
```

### ECDF (no binning decisions, precise percentiles)
```python
fig = px.ecdf(df, x="value", color="group",
              title="Cumulative Distribution",
              labels={"value": "Response Time (ms)"})
fig.update_layout(template="plotly_white")
```

### Ridgeline (many distributions)
```python
# Using Graph Objects for ridgeline
groups = df["group"].unique()
fig = go.Figure()
for i, group in enumerate(groups):
    subset = df[df["group"] == group]["value"]
    fig.add_trace(go.Violin(x=subset, name=group, side="positive",
                            line_color=px.colors.qualitative.Set2[i % 8],
                            meanline_visible=True))
fig.update_traces(orientation="h", width=1.8)
fig.update_layout(template="plotly_white")
```

### 2D density heatmap (overplotted scatter alternative)
```python
fig = px.density_heatmap(df, x="x", y="y", nbinsx=50, nbinsy=50,
                         color_continuous_scale="Viridis",
                         marginal_x="histogram", marginal_y="histogram",
                         title="Joint Distribution (n=100,000)")
fig.update_layout(template="plotly_white")
```

---

## Relationship Charts

### Scatter with trendline
```python
fig = px.scatter(df, x="x", y="y", trendline="ols",
                 color="group", size="magnitude",
                 hover_data=["label"],
                 title="X vs Y with Linear Fit")
fig.update_layout(template="plotly_white")

# Get the regression stats
results = px.get_trendline_results(fig)
print(results.iloc[0]["px_fit_results"].summary())
```

### Scatter with marginal distributions
```python
fig = px.scatter(df, x="x", y="y", color="group",
                 marginal_x="histogram", marginal_y="box",
                 title="Relationship with Marginals")
fig.update_layout(template="plotly_white")
```

### Scatter matrix (EDA on 3-6 variables)
```python
fig = px.scatter_matrix(df, dimensions=["var1", "var2", "var3", "var4"],
                        color="group", opacity=0.6,
                        title="Pairwise Relationships")
fig.update_traces(diagonal_visible=True, showupperhalf=False)
fig.update_layout(template="plotly_white", height=800)
```

### Correlation heatmap
```python
corr = df[numeric_cols].corr()
fig = px.imshow(corr, color_continuous_scale="RdBu",
                color_continuous_midpoint=0, text_auto=".2f",
                title="Feature Correlations",
                aspect="auto")
fig.update_layout(template="plotly_white")
```

### Parallel coordinates (high-dimensional)
```python
fig = px.parallel_coordinates(df,
                               dimensions=["dim1", "dim2", "dim3", "dim4", "metric"],
                               color="metric",
                               color_continuous_scale="Viridis",
                               title="Parameter Space Exploration")
fig.update_layout(template="plotly_white")
```

### Parallel categories (categorical relationships)
```python
fig = px.parallel_categories(df, dimensions=["region", "product", "channel"],
                              color="revenue", color_continuous_scale="Viridis",
                              title="Category Flow")
fig.update_layout(template="plotly_white")
```

### WebGL scatter (5K-50K points)
```python
fig = px.scatter(df, x="x", y="y", color="group",
                 render_mode="webgl", opacity=0.3,
                 title=f"Large Dataset (n={len(df):,})")
fig.update_layout(template="plotly_white")
```

---

## Composition Charts

### Stacked bar
```python
fig = px.bar(df, x="quarter", y="revenue", color="product_line",
             title="Revenue by Product Line",
             text_auto=".2s")
fig.update_layout(template="plotly_white", barmode="stack")
```

### 100% stacked bar (proportions)
```python
# Calculate percentages
df_pct = df.groupby(["quarter", "product"]).sum().groupby(level=0).apply(
    lambda x: x / x.sum() * 100).reset_index()
fig = px.bar(df_pct, x="quarter", y="revenue", color="product",
             title="Revenue Mix (%)", text_auto=".1f")
fig.update_layout(barmode="stack", template="plotly_white")
```

### Treemap (hierarchical part-to-whole)
```python
fig = px.treemap(df, path=["region", "country", "city"], values="revenue",
                 color="growth_rate", color_continuous_scale="RdYlGn",
                 color_continuous_midpoint=0,
                 title="Revenue by Geography")
fig.update_layout(template="plotly_white")
```

### Sunburst (hierarchical drill-down)
```python
fig = px.sunburst(df, path=["division", "department", "team"],
                  values="headcount", color="satisfaction",
                  color_continuous_scale="RdYlGn",
                  title="Organization Structure")
fig.update_layout(template="plotly_white")
```

### Icicle (deep hierarchies)
```python
fig = px.icicle(df, path=["level1", "level2", "level3", "level4"],
                values="size", color="metric",
                title="Deep Hierarchy Breakdown")
fig.update_layout(template="plotly_white")
```

### Waterfall (financial bridge)
```python
fig = go.Figure(go.Waterfall(
    x=["Revenue", "COGS", "Gross Profit", "OpEx", "Taxes", "Net Income"],
    y=[1000, -400, None, -300, -60, None],
    measure=["absolute", "relative", "total", "relative", "relative", "total"],
    text=["+1000", "-400", "600", "-300", "-60", "240"],
    textposition="outside",
    connector={"line": {"color": "grey"}}
))
fig.update_layout(title="P&L Waterfall", template="plotly_white")
```

### Funnel (conversion/dropoff)
```python
fig = px.funnel(df, x="count", y="stage",
                title="Conversion Funnel",
                text_auto=True)
fig.update_layout(template="plotly_white")
```

### Sankey (flows between stages)
```python
fig = go.Figure(go.Sankey(
    node=dict(label=node_labels, color=node_colors, pad=15, thickness=20),
    link=dict(source=source_indices, target=target_indices,
              value=flow_values, color="rgba(100,100,100,0.3)")
))
fig.update_layout(title="User Journey Flow", template="plotly_white")
```

### Pie (only for 2-3 slices)
```python
fig = px.pie(df, values="share", names="category",
             title="Market Share (Top 3 Players)",
             hole=0.3)  # Donut style is slightly better than full pie
fig.update_traces(textinfo="percent+label", textposition="inside")
fig.update_layout(template="plotly_white", showlegend=False)
```

---

## Time Series Charts

### Line chart (the default for temporal data)
```python
fig = px.line(df, x="date", y="value", color="series",
              title="Daily Active Users",
              labels={"value": "DAU", "date": ""})
fig.update_layout(template="plotly_white", hovermode="x unified")
```

### Line with confidence band
```python
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["date"], y=df["upper"], mode="lines",
                         line=dict(width=0), showlegend=False))
fig.add_trace(go.Scatter(x=df["date"], y=df["lower"], mode="lines",
                         line=dict(width=0), fill="tonexty",
                         fillcolor="rgba(68,68,68,0.15)", showlegend=False))
fig.add_trace(go.Scatter(x=df["date"], y=df["mean"], mode="lines",
                         name="Mean", line=dict(color="#636EFA")))
fig.update_layout(template="plotly_white", title="Metric with 95% CI")
```

### Stacked area (composition over time)
```python
fig = px.area(df, x="date", y="value", color="category",
              title="Revenue Composition Over Time")
fig.update_layout(template="plotly_white")
```

### Candlestick (financial OHLC)
```python
fig = go.Figure(go.Candlestick(
    x=df["date"], open=df["open"], high=df["high"],
    low=df["low"], close=df["close"]))
fig.update_layout(title="AAPL Stock Price",
                  xaxis_rangeslider_visible=False,
                  template="plotly_white")
```

### Animated scatter (Gapminder-style)
```python
fig = px.scatter(df, x="gdp_per_cap", y="life_exp",
                 size="population", color="continent",
                 animation_frame="year", animation_group="country",
                 hover_name="country", size_max=60,
                 log_x=True, range_y=[25, 90],
                 title="Development Over Time")
fig.update_layout(template="plotly_white")
```

### Time series with event annotations
```python
fig = px.line(df, x="date", y="value", title="Revenue with Key Events")
events = [("2024-03-15", "Product Launch"), ("2024-06-01", "Price Change")]
for date, label in events:
    fig.add_vline(x=date, line_dash="dash", line_color="grey")
    fig.add_annotation(x=date, y=df["value"].max(), text=label,
                       showarrow=True, arrowhead=2, yshift=10)
fig.update_layout(template="plotly_white")
```

---

## Spatial Charts

### Choropleth (values by region)
```python
fig = px.choropleth(df, locations="iso_alpha", color="gdp",
                    color_continuous_scale="Viridis",
                    hover_name="country",
                    title="GDP by Country")
fig.update_layout(template="plotly_white")
```

### Scatter map (point locations)
```python
fig = px.scatter_map(df, lat="latitude", lon="longitude",
                     size="magnitude", color="category",
                     hover_name="name", zoom=3,
                     title="Event Locations")
fig.update_layout(template="plotly_white")
```

### Density map (event hotspots)
```python
fig = px.density_map(df, lat="latitude", lon="longitude",
                     z="intensity", radius=20,
                     title="Event Density")
fig.update_layout(template="plotly_white")
```

---

## Statistical Patterns

### A/B test bar with error bars
```python
fig = px.bar(results, x="variant", y="conversion_rate",
             error_y="ci_halfwidth", color="variant",
             text_auto=".1%",
             title="A/B Test: Variant B +2.3% (p=0.003)")
fig.update_layout(template="plotly_white", showlegend=False)
```

### QQ plot
```python
from scipy import stats

theoretical = stats.norm.ppf(np.linspace(0.01, 0.99, len(data)))
sample = np.sort(data)

fig = px.scatter(x=theoretical, y=sample,
                 labels={"x": "Theoretical Quantiles", "y": "Sample Quantiles"},
                 title="QQ Plot (Normality Check)")
fig.add_shape(type="line",
              x0=theoretical.min(), x1=theoretical.max(),
              y0=theoretical.min(), y1=theoretical.max(),
              line=dict(dash="dash", color="red"))
fig.update_layout(template="plotly_white")
```

### Confusion matrix
```python
fig = px.imshow(cm, text_auto=True,
                labels=dict(x="Predicted", y="Actual", color="Count"),
                x=class_names, y=class_names,
                color_continuous_scale="Blues",
                title="Confusion Matrix")
fig.update_layout(template="plotly_white")
```

### ROC curve with AUC
```python
fig = px.area(x=fpr, y=tpr,
              labels=dict(x="False Positive Rate", y="True Positive Rate"),
              title=f"ROC Curve (AUC = {auc_score:.3f})")
fig.add_shape(type="line", x0=0, x1=1, y0=0, y1=1,
              line=dict(dash="dash", color="grey"))
fig.update_layout(template="plotly_white")
```

### Feature importance (horizontal sorted bar)
```python
imp = imp.sort_values("importance")
fig = px.bar(imp, x="importance", y="feature", orientation="h",
             title="Top 20 Feature Importances",
             text_auto=".3f")
fig.update_layout(template="plotly_white", yaxis_title=None)
```

---

## The Bridge Pattern

Start with Express for speed, customize with Graph Objects for precision. This is the senior workflow.

```python
# Step 1: Quick chart with Express
fig = px.scatter(df, x="revenue", y="profit", color="region",
                 size="employees", hover_name="company")

# Step 2: Customize with GO-style methods
fig.add_hline(y=0, line_dash="dash", line_color="grey",
              annotation_text="Break-even")
fig.add_vrect(x0=100, x1=200, fillcolor="green", opacity=0.1,
              annotation_text="Target Zone")

# Step 3: Polish layout
fig.update_layout(
    template="plotly_white",
    title=dict(text="Revenue vs Profit by Region", x=0.5),
    xaxis_title="Revenue ($M)",
    yaxis_title="Profit ($M)",
    legend_title="Region",
    font=dict(family="Inter, sans-serif"),
    hoverlabel=dict(bgcolor="white", font_size=12),
)

# Step 4: Custom hover template
fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>"
                  "Revenue: $%{x:.1f}M<br>"
                  "Profit: $%{y:.1f}M<br>"
                  "<extra></extra>"  # Removes trace name box
)

fig.show()
```

### When you MUST use Graph Objects directly

```python
# Mixed trace types in subplots
fig = make_subplots(rows=2, cols=2,
                    subplot_titles=["Revenue Trend", "Distribution",
                                    "By Category", "Correlation"],
                    specs=[[{"type": "xy"}, {"type": "xy"}],
                           [{"type": "xy"}, {"type": "xy"}]])

fig.add_trace(go.Scatter(x=dates, y=revenue, mode="lines", name="Revenue"),
              row=1, col=1)
fig.add_trace(go.Histogram(x=values, name="Distribution"),
              row=1, col=2)
fig.add_trace(go.Bar(x=categories, y=amounts, name="Categories"),
              row=2, col=1)
fig.add_trace(go.Heatmap(z=corr_matrix, x=cols, y=cols,
                         colorscale="RdBu", zmid=0),
              row=2, col=2)

fig.update_layout(height=800, template="plotly_white",
                  title="Dashboard Overview")
fig.show()
```

---

## Layout and Styling

### Clean template setup
```python
# Option 1: Use built-in
fig.update_layout(template="plotly_white")

# Option 2: Create a custom template for consistent branding
import plotly.io as pio

custom_template = go.layout.Template()
custom_template.layout = go.Layout(
    font=dict(family="Inter, sans-serif", size=12, color="#333"),
    title=dict(font=dict(size=16), x=0.5),
    plot_bgcolor="white",
    paper_bgcolor="white",
    colorway=px.colors.qualitative.Set2,
    xaxis=dict(showgrid=True, gridcolor="#eee", zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="#eee", zeroline=False),
    hoverlabel=dict(bgcolor="white", font_size=12),
)
pio.templates["clean"] = custom_template
pio.templates.default = "clean"
```

### Faceting (small multiples)
```python
fig = px.scatter(df, x="x", y="y", color="group",
                 facet_col="region", facet_row="year",
                 facet_col_wrap=3,  # Max columns before wrapping
                 title="Patterns by Region and Year")
fig.update_layout(template="plotly_white")
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))  # Clean facet labels
```

### Hover template customization
```python
# Format numbers, add units, remove trace box
fig.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "Revenue: $%{x:,.0f}<br>"
        "Growth: %{y:.1f}%<br>"
        "Employees: %{marker.size:,}<br>"
        "<extra></extra>"
    )
)
```

---

## Export

### Static images (requires kaleido)
```python
# PNG for slides (2x for retina)
fig.write_image("chart.png", width=1200, height=800, scale=2)

# SVG for web (scalable)
fig.write_image("chart.svg", width=1200, height=800)

# PDF for print
fig.write_image("chart.pdf", width=1200, height=800)
```

### Interactive HTML
```python
# Standalone file (includes plotly.js)
fig.write_html("chart.html", include_plotlyjs=True)

# Lightweight (reference CDN)
fig.write_html("chart.html", include_plotlyjs="cdn")
```

### For Jupyter notebooks
```python
fig.show()  # Renders inline automatically
```
