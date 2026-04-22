---
name: plotly-viz
description: Senior data scientist's guide to Python data visualization with Plotly. Use this skill whenever the user wants to create charts, graphs, plots, dashboards, or any data visualization in Python — even if they don't say "plotly" explicitly. Also use when the user asks which chart type to use, how to visualize data, or needs help setting up a Python data science environment with uv/direnv. Triggers on keywords like plot, chart, graph, visualize, histogram, scatter, heatmap, dashboard, EDA, exploratory analysis, or any data presentation task.
---

# Plotly Data Visualization — Senior Data Scientist's Playbook

You are reasoning like a senior data scientist with deep intuition about data visualization. You don't just make charts — you choose the right chart for the story the data is telling. Every visualization decision has a reason rooted in how humans perceive patterns.

## Environment Setup

When starting a new data science project, initialize with `uv` and `direnv` for zero-friction reproducibility.

### First-time machine setup (once)

```bash
brew install uv direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc

# Create global direnv helper
mkdir -p ~/.config/direnv
cat > ~/.config/direnv/direnvrc << 'EOF'
use_uv() {
    if [ ! -d .venv ]; then
        uv venv
    fi
    source .venv/bin/activate
    uv sync
}
EOF

# Globally ignore .envrc from git
mkdir -p ~/.config/git
echo ".envrc" >> ~/.config/git/ignore
```

### Per-project setup

```bash
mkdir my-analysis && cd my-analysis
uv init --app
uv add plotly pandas numpy scipy kaleido nbformat

# Create .envrc (one line is all you need)
echo "use_uv" > .envrc
direnv allow
```

Now every time you `cd` into the project, the venv activates and deps sync automatically. No more `source .venv/bin/activate`.

### Core dependencies for data science visualization

```
plotly          # Interactive visualization engine
pandas          # DataFrame manipulation
numpy           # Numerical computing
scipy           # Statistical functions (distributions, tests)
kaleido         # Static image export (png, pdf, svg)
nbformat        # Notebook support
scikit-learn    # ML utilities (PCA, clustering, regression)
```

Add only what you need. `plotly + pandas + numpy` is the minimum. Add `scipy` for statistical charts, `scikit-learn` for ML viz.

---

## The Two APIs: Express vs Graph Objects

### Plotly Express (`px`) — Start here, always

Plotly Express is the high-level API. One function call = one chart. It handles 90% of visualization needs with sensible defaults.

```python
import plotly.express as px
fig = px.scatter(df, x="gdp", y="life_exp", color="continent", size="pop")
fig.show()
```

**Use Express when:** you're exploring data, building standard charts, iterating quickly. Express returns a `Figure` object, so you can always customize after.

### Graph Objects (`go`) — When you need full control

Graph Objects is the low-level API. More verbose (5-100x more code) but unlimited customization.

```python
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["date"], y=df["revenue"], mode="lines+markers"))
fig.update_layout(title="Revenue Over Time")
fig.show()
```

**Use Graph Objects when:**
- Combining different trace types in subplots (e.g., bar + line)
- 3D charts like `Mesh3d` or `Isosurface` (no Express equivalent)
- Dual y-axes or complex multi-panel layouts
- Annotations, shapes, or custom interactivity beyond defaults

**The bridge pattern** — start Express, finish with GO:
```python
fig = px.bar(df, x="month", y="sales", color="region")
fig.add_trace(go.Scatter(x=df["month"], y=df["target"], mode="lines", name="Target"))
fig.update_layout(barmode="group", template="plotly_white")
```

This is the senior move: rapid prototyping with Express, surgical customization with Graph Objects.

---

## Choosing the Right Chart: The Decision Framework

Data visualization answers one of four questions. Identify the question first, then pick the chart.

### 1. COMPARISON — "How do values differ?"

| Chart | When | Why this, not something else |
|-------|------|------------------------------|
| **Bar chart** (`px.bar`) | Comparing categories (≤15 items) | Human eyes compare lengths along a common baseline better than any other visual encoding. Horizontal bars when labels are long. |
| **Grouped bar** (`px.bar`, `barmode="group"`) | Comparing subcategories side-by-side | Each group shares a baseline, making within-group comparison intuitive. |
| **Lollipop** (`go.Scatter` + `go.Bar` with width=0) | Same as bar but with many categories | Less ink, less clutter. The dot draws the eye to the value. |
| **Radar/Spider** (`go.Scatterpolar`) | Comparing profiles across 5-10 dimensions | Shows the "shape" of a profile. Use sparingly — hard to read precisely. |
| **Bullet chart** (custom GO) | Comparing actual vs target | Encodes both value and benchmark in minimal space. |

**Why not pie charts for comparison?** Humans are terrible at comparing angles and areas. A bar chart communicating the same data is faster to parse and more accurate. Pie charts are only acceptable for showing 2-3 parts of a whole where the exact values matter less than the general split.

### 2. DISTRIBUTION — "How is my data spread?"

| Chart | When | Why this, not something else |
|-------|------|------------------------------|
| **Histogram** (`px.histogram`) | Single variable distribution | The foundational distribution chart. Choose bin count carefully — too few hides structure, too many creates noise. Use `nbins` or `Freedman-Diaconis` rule. |
| **Box plot** (`px.box`) | Comparing distributions across groups | Shows median, IQR, and outliers at a glance. Best for 3-15 groups. |
| **Violin plot** (`px.violin`) | Distribution shape matters | Shows the full density curve, not just summary stats. Reveals bimodality that box plots hide. |
| **Strip/Jitter plot** (`px.strip`) | Small datasets (n < 200) | Shows every individual point. Combines well with box/violin via `points="all"`. |
| **Histogram 2D / Density heatmap** (`px.density_heatmap`) | Joint distribution of 2 variables | When scatter plots become overplotted (n > 5000), density encoding reveals structure. |
| **ECDF** (`px.ecdf`) | Comparing cumulative distributions | No binning decisions needed. Precise percentile reads. Two ECDFs overlaid = instant visual KS test. |
| **Ridgeline** (multiple `go.Violin` stacked) | Comparing many distributions | Shows distribution evolution across a category (e.g., income by decade). Beautiful and compact. |

**Why violin over box?** A box plot of a bimodal distribution looks unimodal. The violin shows the truth. Always prefer violin when the shape of the distribution carries meaning.

### 3. RELATIONSHIP — "How are variables connected?"

| Chart | When | Why this, not something else |
|-------|------|------------------------------|
| **Scatter plot** (`px.scatter`) | 2 continuous variables | The workhorse of relationship analysis. Add `trendline="ols"` for regression. Use `color` for a third variable, `size` for a fourth. |
| **Bubble chart** (`px.scatter` with `size=`) | 3 continuous variables | Encodes a third dimension as area. Human area perception is imprecise, so use for relative comparison, not exact values. |
| **Heatmap** (`px.imshow`) | Correlation matrix or 2D aggregated data | Color encodes magnitude across a grid. Use diverging colorscale (`RdBu`) centered at 0 for correlations. |
| **Scatter matrix** (`px.scatter_matrix`) | EDA on 3-6 variables | Quick overview of all pairwise relationships. The first thing to run when exploring a new dataset. |
| **Parallel coordinates** (`px.parallel_coordinates`) | Relationships across many dimensions | Each axis is a variable. Lines that cluster together reveal groups. Use for feature selection and outlier detection. |
| **Parallel categories** (`px.parallel_categories`) | Flow between categorical variables | Shows how categories co-occur. Think Sankey but for categorical relationships. |

**Why scatter over line?** Lines imply continuity and order (e.g., time). Scatter shows relationship without implying causation or sequence.

### 4. COMPOSITION — "What makes up the whole?"

| Chart | When | Why this, not something else |
|-------|------|------------------------------|
| **Stacked bar** (`px.bar`, `barmode="stack"`) | Composition across categories | Shows both the total and the parts. Absolute values visible. |
| **100% stacked bar** (normalize data first) | Comparing proportions across groups | Removes the total, focuses on relative share. Use when totals differ significantly. |
| **Pie chart** (`px.pie`) | 2-3 slices, casual audience | Only when rough proportions suffice and the audience expects a pie. Never for precise comparison. |
| **Treemap** (`px.treemap`) | Hierarchical composition | Shows nested part-to-whole. Better than nested pies. Use for file sizes, org budgets, category breakdowns. |
| **Sunburst** (`px.sunburst`) | Hierarchical composition with drill-down | Like treemap but radial. Better for interactive exploration of 2-3 hierarchy levels. |
| **Icicle** (`px.icicle`) | Deep hierarchies | Linear layout is easier to read than sunburst for >3 levels. |
| **Waterfall** (`go.Waterfall`) | Cumulative effect of sequential values | Shows how values add/subtract to reach a total. Perfect for financial bridges (revenue → profit). |
| **Funnel** (`px.funnel`) | Sequential dropoff | Conversion rates, pipeline stages. The narrowing shape immediately communicates loss at each stage. |

### 5. CHANGE OVER TIME — "What's the trend?"

| Chart | When | Why this, not something else |
|-------|------|------------------------------|
| **Line chart** (`px.line`) | 1-7 time series | The default for temporal data. Lines imply continuity and ordered progression. |
| **Area chart** (`px.area`) | Stacked time series showing volume | Fills emphasize magnitude. Stacked areas show both individual and total contribution. |
| **Candlestick** (`go.Candlestick`) | Financial OHLC data | Encodes open/high/low/close in a single glyph. The standard for trading analysis. |
| **Animated scatter** (`px.scatter`, `animation_frame=`) | Change across a third time dimension | Gapminder-style. Shows evolution while preserving x/y relationship. Compelling for presentations. |

**Why not bar charts for time?** Bars imply discrete, independent values. Lines convey the continuity of time. Use bars for time only when the intervals are truly discrete and non-adjacent (e.g., comparing Q1 across years).

### 6. SPATIAL — "Where?"

| Chart | When | Why this, not something else |
|-------|------|------------------------------|
| **Choropleth** (`px.choropleth` / `px.choropleth_map`) | Values by region/country | Color-encodes a metric across geographic boundaries. Be careful: large regions dominate visually regardless of value. |
| **Scatter map** (`px.scatter_map`) | Point locations with magnitude | Plots points on a real map. Size/color encode variables. Better than choropleth when data is at point-level. |
| **Density map** (`px.density_map`) | Event concentration | Heatmap on geography. Shows hotspots. Better than scatter when points overlap heavily. |
| **Line map** (`px.line_map`) | Routes, flows, connections | Origin-destination visualization. Flight paths, supply chains. |

---

## Senior Patterns and Intuition

### Template and Theme

Always set a clean template. `plotly_white` is the professional default:
```python
import plotly.io as pio
pio.templates.default = "plotly_white"
```

### Color with Purpose

```python
# Categorical: use Plotly's built-in qualitative scales
fig = px.bar(df, x="category", y="value", color="group",
             color_discrete_sequence=px.colors.qualitative.Set2)

# Sequential (magnitude): blues, viridis, or plasma
fig = px.choropleth(df, color="gdp", color_continuous_scale="Viridis")

# Diverging (deviation from center): RdBu, RdYlGn
fig = px.imshow(corr_matrix, color_continuous_scale="RdBu", zmin=-1, zmax=1)
```

**Why Viridis?** It's perceptually uniform (equal steps in data = equal steps in perceived color), colorblind-safe, and prints well in grayscale. Use it as your default sequential scale.

### Faceting Over Overplotting

When you have too many groups on one chart, facet:
```python
fig = px.scatter(df, x="x", y="y", facet_col="category", facet_col_wrap=3)
```

Faceting splits data into small multiples — same scale, same encoding, easy comparison. It's almost always better than cramming everything into one plot with a 20-item legend.

### The Data-Ink Ratio

Remove visual elements that don't carry data. Gridlines, borders, tick marks — question each one:
```python
fig.update_layout(
    plot_bgcolor="white",
    xaxis=dict(showgrid=False, showline=True, linewidth=1),
    yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor="lightgray"),
    margin=dict(l=40, r=20, t=40, b=40),
)
```

### Hover and Interactivity

Plotly's interactivity is its superpower. Customize hover templates:
```python
fig.update_traces(
    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>"
)
```

The `<extra></extra>` removes the trace name box. Small detail, big polish.

### Export for Different Audiences

```python
# Interactive HTML (for colleagues, dashboards)
fig.write_html("report.html", include_plotlyjs="cdn")

# Static PNG (for slides, documents)
fig.write_image("chart.png", width=1200, height=600, scale=2)

# Static PDF (for print)
fig.write_image("chart.pdf")
```

Requires `kaleido` for static export — that's why we include it in the project deps.

### Common Anti-Patterns to Avoid

1. **3D bar charts** — Never. They distort values through perspective. Use grouped 2D bars.
2. **Dual y-axes** — Almost always confusing. Use faceted subplots or normalize the data instead. If you must, make the axes visually distinct (color-code them).
3. **Too many colors** — If your legend has more than 7 items, rethink the design. Facet, aggregate, or highlight only the interesting categories.
4. **Truncated y-axis** — Starting the y-axis at non-zero exaggerates differences. Always start at 0 for bar charts. Line charts can start elsewhere if labeled clearly.
5. **Rainbow colormaps** — Rainbow (jet) is not perceptually uniform and misleads. Use Viridis, Plasma, or domain-appropriate diverging scales.

---

## Quick Reference: "I have X, show me Y"

| Your data looks like... | Chart | Code pattern |
|------------------------|-------|--------------|
| One numeric column | Histogram | `px.histogram(df, x="col")` |
| One categorical column | Bar (value counts) | `px.bar(df["col"].value_counts().reset_index(), x="col", y="count")` |
| Two numeric columns | Scatter | `px.scatter(df, x="a", y="b")` |
| Numeric across groups | Box or Violin | `px.violin(df, x="group", y="value", box=True)` |
| Time + numeric | Line | `px.line(df, x="date", y="value")` |
| Categories + numeric | Bar | `px.bar(df, x="category", y="value")` |
| Parts of a whole | Treemap or Stacked bar | `px.treemap(df, path=["a","b"], values="v")` |
| Correlation matrix | Heatmap | `px.imshow(df.corr(), color_continuous_scale="RdBu")` |
| Geographic points | Scatter map | `px.scatter_map(df, lat="lat", lon="lon", size="val")` |
| Geographic regions | Choropleth | `px.choropleth(df, locations="iso", color="val")` |
| High-dimensional data | Parallel coordinates | `px.parallel_coordinates(df, dimensions=[...])` |
| Hierarchical categories | Sunburst or Treemap | `px.sunburst(df, path=["a","b","c"], values="v")` |
| Flow between stages | Sankey | `go.Sankey(node=..., link=...)` |
| Financial OHLC | Candlestick | `go.Candlestick(x=dates, open=o, high=h, low=l, close=c)` |

---

## Reference Files

For deeper guidance on specific topics, see:
- `references/chart-decision-tree.md` — Extended decision flowchart for edge cases
