# Executive Dashboard Recommendation: Quarterly Customer Transaction Review

## 1. Understanding the Question

Your VP wants answers to the quarterly review's core questions, which map to three of the six fundamental visualization question types:

| VP's likely question | Visualization question type |
|---|---|
| "How is revenue trending?" | **Change over time** |
| "Which categories/regions are performing?" | **Comparison** |
| "What's our revenue mix?" | **Composition** |
| "Are there patterns across regions and categories?" | **Relationship** (category interactions) |

## 2. Data Characterization

| Property | Value | Implication |
|---|---|---|
| Rows | 50,000 | Mid-large -- bar/line aggregations are fine; scatter needs WebGL or aggregation |
| `date` | Temporal | Time series -- line charts for trend |
| `amount` | Numeric (continuous) | The metric to aggregate (sum, mean, count) |
| `category` | Categorical (12 levels) | At the upper bound for color encoding (max ~7 distinguishable). Facet or use top-N + highlight. |
| `region` | Categorical (4 levels) | Excellent for color encoding or facet_col -- 4 is well within perceptual limits |

## 3. Audience Analysis

Your audience is a **VP at a quarterly review** -- this is the textbook executive audience.

**Executive dashboard rules (from perception science):**
- Answer "how are we doing?" in under 5 seconds per chart
- Max 4-6 charts per view -- no more than 2-3 chart types
- Title each chart with **the insight**, not the metric name (e.g., "Revenue grew 12% QoQ" not "Quarterly Revenue")
- **Use:** KPI cards, bar charts, line charts, waterfall
- **Avoid:** Violin plots, parallel coordinates, scatter matrices, ECDF, heatmaps -- anything requiring statistical literacy

## 4. Recommended Dashboard Layout

Follow the **Z-pattern**: most important chart top-left, summary KPIs across the top, detail below.

### Row 1: KPI Cards (Big Numbers)

Four KPI cards across the top, one per key metric:

| Card | Content | Example |
|---|---|---|
| Total Revenue | Sum of `amount` this quarter, with QoQ % change | "$4.2M (+12% QoQ)" |
| Transaction Count | Count of rows, with QoQ % change | "50,000 (+8% QoQ)" |
| Avg Transaction | Mean `amount`, with QoQ % change | "$84 (+3.7% QoQ)" |
| Top Category | Category with highest revenue | "Electronics: $890K" |

**Why KPI cards:** Executives want the headline number instantly. Pre-attentive processing of large, isolated numbers is under 250ms -- faster than any chart.

### Row 2, Left: Line Chart -- Revenue Trend Over Time

**Chart:** Line chart with 4 lines (one per region), x = date (aggregated to week or month), y = sum of `amount`.

**Why line chart over bar chart:** Lines imply continuity and temporal ordering -- exactly what time series data has. The brain naturally traces trends (slopes) pre-attentively. Bars would imply discrete, independent intervals and clutter the view with 4 regions.

**Why 4 lines work:** With only 4 regions, each line gets a distinct, easily distinguishable color. This stays well under the 7-color limit where pre-attentive color discrimination breaks down.

```python
import plotly.express as px
import pandas as pd

df["date"] = pd.to_datetime(df["date"])
df_weekly = df.groupby([pd.Grouper(key="date", freq="W"), "region"])["amount"].sum().reset_index()

fig = px.line(df_weekly, x="date", y="amount", color="region",
              title="Revenue Up 12% QoQ -- West Region Leading Growth",
              labels={"amount": "Revenue ($)", "date": ""})
fig.update_layout(template="plotly_white", hovermode="x unified",
                  legend_title="Region")
fig.show()
```

**Senior touch:** Use `hovermode="x unified"` so all four region values appear in a single tooltip on hover. Annotate significant events (promotions, holidays) with `fig.add_vline()`.

### Row 2, Right: Horizontal Bar Chart -- Revenue by Category

**Chart:** Horizontal bar, sorted by value descending, showing total `amount` per category.

**Why horizontal sorted bar:** Cleveland & McGill (1984) proved that humans decode aligned lengths on a common baseline more accurately than any other encoding except position. Sorting by value makes the ranking immediately visible -- the ranking IS the insight. Horizontal orientation accommodates the 12 category labels without rotation (humans read left-to-right labels faster than rotated vertical ones).

**Why not pie chart:** With 12 categories, a pie chart would be unreadable. Pie is only acceptable for 2-3 slices. Angle encoding (5-15% error) is far less accurate than length encoding (2-5% error).

```python
df_cat = df.groupby("category")["amount"].sum().reset_index().sort_values("amount")

fig = px.bar(df_cat, x="amount", y="category", orientation="h",
             title="Electronics and Apparel Drive 45% of Revenue",
             text="amount", text_auto="$.2s")
fig.update_layout(template="plotly_white", yaxis_title=None)
fig.show()
```

**Senior touch:** Consider the "highlight and grey" pattern -- color the top 2-3 categories and grey out the rest. This leverages pre-attentive pop-out: the colored bars instantly draw the VP's eye to what matters.

### Row 3, Left: Grouped Bar Chart -- Category Performance by Region

**Chart:** Grouped bar with `region` on x-axis, `amount` on y-axis, `color` = top 5 categories (aggregate the remaining 7 into "Other").

**Why grouped bar:** The VP will ask "how does each region's mix compare?" Grouped bars let the eye compare subcategories within each region (same cluster) and across regions (same color). This is the standard executive chart for cross-dimensional comparison.

**Why top 5 + Other:** 12 categories would produce 12 colors, far exceeding the 7-color perceptual limit. Aggregating to top 5 + Other keeps it at 6 distinct colors -- clean, readable, and still captures the dominant story.

```python
top5 = df.groupby("category")["amount"].sum().nlargest(5).index.tolist()
df["cat_grouped"] = df["category"].where(df["category"].isin(top5), "Other")

df_grouped = df.groupby(["region", "cat_grouped"])["amount"].sum().reset_index()

fig = px.bar(df_grouped, x="region", y="amount", color="cat_grouped",
             barmode="group",
             title="West Leads in Electronics; South Dominates Apparel",
             text_auto="$.2s")
fig.update_layout(template="plotly_white", legend_title="Category")
fig.show()
```

### Row 3, Right: Stacked Bar or Treemap -- Revenue Composition

**Option A: Stacked bar** by quarter (if you have multi-quarter data for comparison) showing category composition within each region.

**Option B: Treemap** with path `[region, category]` for a single-quarter snapshot -- this shows the hierarchical part-to-whole relationship and lets the VP visually grasp which region-category combinations dominate.

```python
# Option A: Stacked bar (composition across regions)
df_comp = df.groupby(["region", "cat_grouped"])["amount"].sum().reset_index()

fig = px.bar(df_comp, x="region", y="amount", color="cat_grouped",
             title="Revenue Composition: West Region Most Diversified",
             text_auto="$.2s")
fig.update_layout(barmode="stack", template="plotly_white", legend_title="Category")
fig.show()
```

```python
# Option B: Treemap (hierarchical drill-down)
df_tree = df.groupby(["region", "category"])["amount"].sum().reset_index()

fig = px.treemap(df_tree, path=["region", "category"], values="amount",
                 title="Revenue Breakdown: Region > Category")
fig.update_layout(template="plotly_white")
fig.show()
```

**Why stacked bar over pie:** Stacked bar encodes with length (accurate) and shows totals. Pie encodes with angle (inaccurate) and can't show absolute totals. With 4 regions, stacked bar keeps the chart clean.

**Why treemap works here:** Treemaps use area encoding (less precise than length), but for an executive wanting to see the overall structure of "where does revenue come from?", the visual weight of large tiles communicates the hierarchy effectively. Interactive hover compensates for area imprecision by providing exact numbers.

## 5. Anti-Patterns to Avoid

| Temptation | Why it fails | Do this instead |
|---|---|---|
| Pie chart with 12 slices | Angles are inaccurate; 12 slices makes comparison impossible | Horizontal sorted bar |
| 3D bar chart | Perspective distorts values; impossible to compare accurately | Flat grouped 2D bar |
| Dual y-axis (revenue + count on same chart) | Scale relationship is arbitrary; confusing to read | Two separate charts (faceted subplots) or KPI cards |
| 12 colors for 12 categories | Exceeds the 7-color pre-attentive limit; legend becomes a lookup table | Top 5 + "Other", or highlight + grey-out |
| Truncated y-axis on bar charts | Destroys the length-to-value encoding; differences appear up to 400% larger | Always start bar y-axis at 0 |
| Rainbow/jet colormap | Perceptually non-uniform; creates false discontinuities at yellow | Use Plotly's default qualitative palette or Set2 |

## 6. Color Strategy

- **Regions (4 values):** Use a qualitative palette (Set2 or Plotly default). Four colors are well within the distinguishable range.
- **Categories (when shown):** Top 5 + Other with qualitative colors. Keep "Other" as light grey.
- **Consistent encoding across all charts:** If "West" is blue in the line chart, "West" must be blue in the grouped bar and stacked bar. The Gestalt principle of similarity means viewers will instantly map the same color to the same meaning across charts.

## 7. Export Strategy

For the quarterly review presentation:

```python
# PNG at 2x scale for slide deck (retina-quality)
fig.write_image("chart.png", width=1200, height=600, scale=2)

# Interactive HTML for follow-up exploration after the meeting
fig.write_html("dashboard.html", include_plotlyjs="cdn")
```

Requires the `kaleido` package for static image export.

## 8. Project Setup

```bash
mkdir quarterly-dashboard && cd quarterly-dashboard
uv init --app
uv add plotly pandas numpy kaleido
echo "use_uv" > .envrc
direnv allow
```

If the VP wants a live, self-serve dashboard (filtering by region, drilling into categories), upgrade to Dash:

```bash
uv add dash
```

## 9. Summary: The Final Dashboard

| Position | Chart | Question answered | Chart type rationale |
|---|---|---|---|
| **Top row** | 4 KPI cards | "How are we doing overall?" | Big numbers processed in <250ms |
| **Row 2, left** | Line chart (4 region lines) | "What's the trend?" | Lines imply continuity; 4 colors are clean |
| **Row 2, right** | Horizontal sorted bar (12 categories) | "Which categories drive revenue?" | Length on common baseline is the most accurate comparison encoding |
| **Row 3, left** | Grouped bar (region x top 5 categories) | "How do regions compare by category?" | Subcategory comparison within and across groups |
| **Row 3, right** | Stacked bar or treemap | "What's the revenue mix?" | Shows part-to-whole composition |

This dashboard answers the four questions your VP cares about, uses only chart types that executives process intuitively, keeps the color count within perceptual limits, and follows the Z-pattern layout so the most important information hits first.
