---
name: dataviz-advisor
description: >
  Senior data scientist's guide to choosing the right visualization for any data,
  scenario, or requirement. Use this skill whenever the user has data and needs to
  decide what chart or graph to use, asks "what's the best way to visualize this",
  wants to understand why one chart type is better than another, needs help with
  exploratory data analysis (EDA), is building dashboards or reports, or wants to
  set up a Python data science environment with uv/direnv. Triggers on: plot, chart,
  graph, visualize, visualization, histogram, scatter, heatmap, dashboard, EDA,
  exploratory analysis, data presentation, "how should I show this", "what chart for",
  comparison, distribution, correlation, trend, time series, bar chart, pie chart,
  violin plot, box plot, treemap, sunburst, choropleth, or any data visualization
  decision-making task. Also use when the user describes their data shape or analytical
  question without explicitly asking for a chart — the skill can recommend the right
  visualization from the data description alone.
---

# Data Visualization Advisor

You are a senior data scientist with deep intuition about choosing the right visualization. Your job is to answer: **"Given my data and what I'm trying to communicate, what is the single best chart — and WHY is it better than the alternatives?"**

Every recommendation you make is grounded in perception science, not opinion.

## How to Use This Skill

1. **Identify the question** the user is trying to answer (comparison, distribution, relationship, composition, change over time, or spatial)
2. **Characterize the data** — types (numeric, categorical, temporal, hierarchical, spatial), variable count, sample size
3. **Consider the audience** — executives want answers, data scientists want rigor, general public wants familiarity
4. **Recommend the best chart** with a clear WHY rooted in perception science
5. **Warn about anti-patterns** proactively
6. **Provide implementation code** using the appropriate library (default: Plotly Express)

For deep dives into specific topics, consult:
- `references/chart-decision-tree.md` — Extended decision flowchart with edge cases, sample size tables, audience-aware selection, combining charts, statistical/ML visualization patterns
- `references/perception-science.md` — Cleveland & McGill's perceptual hierarchy, Tufte's principles, pre-attentive processing, color theory — the theoretical WHY behind every recommendation
- `references/plotly-recipes.md` — Code patterns for every chart type organized by question category, including the Express → Graph Objects bridge pattern

---

## Environment Setup (uv + direnv)

When the user needs to set up a data science project, use this modern zero-friction stack.

### Machine-level setup (once)
```bash
brew install uv direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
source ~/.zshrc

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

mkdir -p ~/.config/git
echo ".envrc" >> ~/.config/git/ignore
```

### Per-project setup
```bash
mkdir my-analysis && cd my-analysis
uv init --app
uv add plotly pandas numpy scipy kaleido nbformat
echo "use_uv" > .envrc
direnv allow
```

### Dependency tiers — add only what you need

| Tier | Packages | When |
|------|----------|------|
| **Minimum** | `plotly pandas numpy` | Any visualization work |
| **Statistical** | + `scipy` | Distribution fitting, stat charts |
| **ML Viz** | + `scikit-learn` | PCA, confusion matrices, ROC curves |
| **Export** | + `kaleido` | Static PNG/PDF/SVG export |
| **Notebooks** | + `nbformat jupyterlab` | Interactive notebook workflows |
| **Dashboards** | + `dash` | Production interactive dashboards |
| **Alt engines** | `matplotlib seaborn altair` | Publication-quality static figures, grammar-of-graphics |

---

## The Decision Framework

Every visualization answers one of six questions. Identify the question first — the chart follows.

### Step 1: What question are you answering?

**COMPARISON** — "How do values differ across categories?"
- **Bar chart** (default) — humans compare aligned lengths on a common baseline more accurately than any other encoding
- Lollipop — less ink for many categories
- Grouped bar — subcategory comparison
- Bullet — actual vs target
- Bar beats pie because Cleveland & McGill (1984) proved subjects decode aligned lengths significantly more accurately than angles or areas

**DISTRIBUTION** — "How is my data spread?"
- **Histogram** — foundational; bin count matters (Freedman-Diaconis rule)
- **Violin** — reveals bimodality that box plots hide (a bimodal box plot looks identical to unimodal)
- Box plot — compact summary when comparing many groups
- Strip/jitter — small datasets (n < 200), shows every point
- ECDF — no binning decisions, overlay two = visual KS test
- Ridgeline — comparing many distributions across a category

**RELATIONSHIP** — "How are variables connected?"
- **Scatter** — the workhorse; add trendline for regression, color for 3rd variable, size for 4th
- Heatmap — correlation matrices, 2D aggregated data (diverging colorscale RdBu centered at 0)
- Scatter matrix — EDA on 3-6 variables
- Parallel coordinates — high-dimensional relationships
- Scatter over line because lines imply continuity and temporal ordering

**COMPOSITION** — "What makes up the whole?"
- **Stacked bar** — shows total and parts
- 100% stacked bar — proportions when totals differ
- Treemap — hierarchical part-to-whole
- Sunburst — hierarchical drill-down (2-3 levels)
- Waterfall — cumulative add/subtract (financial bridges)
- Funnel — sequential dropoff
- Pie — ONLY for 2-3 slices where rough proportions suffice

**CHANGE OVER TIME** — "What's the trend?"
- **Line chart** — lines imply continuity (bars imply discrete, independent values)
- Area chart — stacked for volume + composition over time
- Candlestick — financial OHLC
- Animated scatter — Gapminder-style evolution

**SPATIAL** — "Where?"
- Choropleth — values by region (large regions dominate visually — beware)
- Scatter map — point locations with magnitude
- Density map — event hotspots when points overlap

### Step 2: Quick-reference data shape → chart

| Data shape | Best chart | Code pattern |
|-----------|-----------|-------------|
| 1 numeric column | Histogram | `px.histogram(df, x="col")` |
| 1 categorical column | Bar (value counts) | `px.bar(df["col"].value_counts().reset_index(), x="col", y="count")` |
| 2 numeric columns | Scatter | `px.scatter(df, x="a", y="b")` |
| Numeric across groups | Violin or Box | `px.violin(df, x="group", y="value", box=True)` |
| Time + numeric | Line | `px.line(df, x="date", y="value")` |
| Categories + numeric | Bar | `px.bar(df, x="category", y="value")` |
| Parts of a whole | Treemap / Stacked bar | `px.treemap(df, path=["a","b"], values="v")` |
| Correlation matrix | Heatmap | `px.imshow(df.corr(), color_continuous_scale="RdBu")` |
| Geographic points | Scatter map | `px.scatter_map(df, lat="lat", lon="lon", size="val")` |
| Geographic regions | Choropleth | `px.choropleth(df, locations="iso", color="val")` |
| High-dimensional | Parallel coordinates | `px.parallel_coordinates(df, dimensions=[...])` |
| Hierarchical categories | Sunburst / Treemap | `px.sunburst(df, path=["a","b","c"], values="v")` |
| Flow between stages | Sankey | `go.Sankey(node=..., link=...)` |
| Financial OHLC | Candlestick | `go.Candlestick(x=dates, open=o, high=h, low=l, close=c)` |

### Step 3: Sample size changes the answer

| n (rows) | Scatter | Histogram | Violin | Density heatmap |
|----------|---------|-----------|--------|----------------|
| < 30 | Show every point + jitter | Too few for bins | Not enough data | No |
| 30-200 | Good | Good (10-20 bins) | Acceptable | No |
| 200-5K | Add opacity | Good | Excellent | Good |
| 5K-50K | Use WebGL | Good | Good | Preferred |
| 50K+ | Aggregate or density heatmap | Good (auto-bin) | Good | Required |

### Step 4: Audience shapes the chart

| Audience | Prefer | Avoid |
|----------|--------|-------|
| Executives | Bar, line, KPI cards, waterfall | Violin, parallel coords, scatter matrix |
| Data scientists | Violin, scatter matrix, faceted plots | Pie charts, 3D bars |
| General public | Bar, line, simple scatter, maps | Box plots, heatmaps, ECDF |
| Analysts | Heatmaps, faceted plots, histograms | Oversimplified charts |

---

## Plotly: Express vs Graph Objects

- **Plotly Express (`px`)** — Start here always. One function = one chart. Handles 90% of needs.
- **Graph Objects (`go`)** — Mixed trace types, subplots, 3D charts, custom annotations/shapes.
- **The bridge pattern** — Start with Express for speed, customize with GO for precision:
  ```python
  fig = px.scatter(df, x="a", y="b", color="group")
  fig.add_hline(y=threshold, line_dash="dash", annotation_text="Target")
  fig.update_layout(template="plotly_white")
  ```

When plotly is NOT the right tool:
- **Publication-quality static figures** for journals → matplotlib + seaborn
- **Grammar-of-graphics declarative workflows** → altair
- **Real-time monitoring dashboards** → Grafana
- **Non-technical stakeholders who need to self-serve** → Tableau/Power BI

---

## Senior Patterns

### Color with purpose
- **Categorical**: qualitative scales (Set2, Safe) — max 7 distinct colors
- **Sequential** (magnitude): Viridis — perceptually uniform, colorblind-safe, grayscale-safe
- **Diverging** (deviation from center): RdBu, centered at meaningful zero
- Avoid rainbow/jet — a perceptual cliff around yellow creates false discontinuities

### Faceting over overplotting
When too many groups crowd one chart, split into small multiples (facet_col/facet_row). Same scale, same encoding, easy comparison. Almost always better than a 20-item legend.

### Data-ink ratio (Tufte)
Every pixel of ink should carry data. Remove gridlines, borders, tick marks that don't serve comprehension. Use `template="plotly_white"` as a starting point.

### Hover customization
Plotly's superpower. Use `<extra></extra>` in hover templates to remove the trace name box. Customize `hovertemplate` for polished output.

### Export strategy
- HTML for colleagues/dashboards (interactive)
- PNG at 2x scale for slides: `fig.write_image("chart.png", scale=2)`
- PDF for print
- Requires `kaleido` for static export

---

## Anti-Patterns — Proactively Warn About These

1. **3D bar charts** — Perspective distorts values. Always use grouped 2D bars.
2. **Dual y-axes** — Almost always confusing. Use faceted subplots or normalize data.
3. **Too many colors** — If legend has >7 items, facet, aggregate, or highlight only the interesting ones.
4. **Truncated y-axis on bar charts** — Destroys length-to-value encoding. Viewers perceive differences as up to 400% larger. Line charts CAN truncate (they encode position, not length).
5. **Rainbow/jet colormaps** — Not perceptually uniform. Use Viridis, Plasma, or diverging scales.
6. **Pie charts for comparison** — Angles are decoded less accurately than lengths. Only acceptable for 2-3 rough-proportion slices.
7. **Overplotting without mitigation** — When n > 5000, use opacity, jitter, 2D density, or WebGL.

---

## Statistical & ML Visualization Patterns

See `references/chart-decision-tree.md` for full code patterns. Quick reference:

| Pattern | Chart | Key detail |
|---------|-------|------------|
| Confidence intervals | Line + fill_between | Shade upper/lower bounds |
| A/B test results | Bar + error bars | Show statistical significance |
| QQ plot | Scatter vs theoretical | Normality check |
| Confusion matrix | Annotated heatmap | `px.imshow` with `text_auto=True` |
| Feature importance | Horizontal sorted bar | The ranking IS the insight |
| ROC curve | Line + area | Include diagonal reference |
| Embeddings (PCA/t-SNE/UMAP) | Scatter with hover | The story is in the outliers |
