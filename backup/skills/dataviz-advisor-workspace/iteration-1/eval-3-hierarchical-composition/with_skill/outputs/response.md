# Visualization Recommendation: Revenue Breakdown by Product Line and Region Over 4 Quarters

## Understanding Your Question

You are asking a **composition** question with a **temporal** dimension: "What makes up our total revenue, broken down hierarchically (product line then region), and how has that composition changed over time?" This involves:

- **Hierarchical categories**: Product line (level 1) and region within each product line (level 2)
- **Temporal axis**: 4 quarters (discrete time intervals)
- **Numeric value**: Revenue

This is one of the most common and nuanced business visualization scenarios because it combines part-to-whole composition, hierarchical nesting, and change over time.

---

## Recommendation: Stacked Bar Chart with Faceting by Product Line

**The best single chart: A faceted stacked bar chart** -- one panel (facet) per product line, with quarters on the x-axis, revenue on the y-axis, and region encoded as color within each stack.

### Why This Is the Best Choice

1. **Bar charts use length encoding (Cleveland & McGill rank 3)**, which humans decode with ~2-5% error. This is far more accurate than area (treemap, ~10-25% error) or angle (sunburst, ~5-15% error).

2. **Stacked bars show both the total and its parts.** Each bar gives you the total revenue for that product line in that quarter, while the colored segments reveal the regional breakdown. The total height answers "how is this product line doing overall?" and the segments answer "which regions contribute?"

3. **Faceting (small multiples) prevents overplotting.** Cramming all product lines and regions into a single chart would create a cluttered, unreadable stacked bar with too many segments. One facet per product line keeps each panel clean and focused, while still enabling cross-product-line comparison because all panels share the same y-axis scale.

4. **Discrete quarters are best shown as bars, not lines.** Lines imply continuity between data points. Quarterly revenue is a discrete aggregate -- there is no meaningful "value" between Q3 and Q4. Bars correctly communicate this discreteness.

5. **Temporal progression reads naturally left-to-right.** Quarters on the x-axis follow the natural reading order, making trends immediately visible.

### Perception Science Basis

- **Length on a common baseline** (the bottom segment of each stack) is highly accurate for the largest region per product line. Upper segments are harder to compare precisely because they sit on varying baselines -- this is a known limitation of stacked bars. The mitigation: faceting means each panel only has a handful of region segments, keeping cognitive load manageable.
- **Color hue** (qualitative, max ~7 categories) distinguishes regions pre-attentively. With most companies having 3-6 regions, this stays well within the 7-color limit.
- **Small multiples** (Tufte) leverage the eye's ability to compare identical visual structures across panels -- the viewer learns the template once and applies it to every facet.

---

## Alternatives Considered and Why They Are Worse

### Sunburst Chart
A sunburst can show the hierarchy (product line -> region) with interactive drill-down, but it **cannot show change over time**. You would need four separate sunbursts (one per quarter), which destroys comparison ability. Sunburst also uses angle/area encoding, which is significantly less accurate than length. It is better suited for a single-point-in-time deep hierarchy, not temporal composition.

### Treemap
Same problem as sunburst: excellent for a single snapshot of hierarchical composition, but it has no natural temporal axis. Four treemaps side by side are very hard to compare because rectangle positions shift between frames. Area encoding (~10-25% error) is also less precise than length.

### Single Stacked Bar (All Product Lines Combined)
This would stack regions within product lines within quarters in a single chart. With, say, 5 product lines and 4 regions each, that is 20 colored segments per bar. This violates the 7-color maximum and makes comparison nearly impossible. Faceting solves this.

### Grouped Bar Chart
Grouped bars place bars side-by-side instead of stacking. This makes individual region values easier to compare but **loses the part-to-whole story** -- you cannot see the total at a glance. Since "how does revenue break down" implies part-to-whole, stacked is the better fit.

### Stacked Area Chart
Stacked area implies continuous change between quarters, which is misleading for discrete quarterly data. Area also suffers from the same baseline problem as stacked bars, but without the clean visual separation that discrete bars provide.

### 100% Stacked Bar
Use this variant **only if** you care about proportional mix and the absolute totals differ so much that they distort the visual. For example, if one product line does $100M and another does $5M, the $5M bar would be too small to read regional segments. In that case, 100% stacked normalizes everything to proportions. But if totals are reasonably comparable, regular stacked bars are better because they preserve the absolute magnitude -- which usually matters for revenue.

---

## Anti-Pattern Warnings

1. **Do not use 3D bars.** Perspective distortion makes comparison impossible. Always use flat 2D bars.
2. **Do not truncate the y-axis.** Bar charts must start at zero. Truncation destroys the length-to-value encoding and inflates perceived differences by up to 400%.
3. **Keep region colors under 7.** If you have more than 7 regions, aggregate the smallest ones into "Other."
4. **Do not use a rainbow/jet colormap for regions.** Use a qualitative palette like Set2 or Plotly's default qualitative colors for categorical data.

---

## Implementation Code (Plotly Express)

```python
import plotly.express as px
import pandas as pd

# Sample data structure
data = {
    "Quarter": ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025"] * 12,
    "Product Line": (["Software"] * 4 + ["Hardware"] * 4 + ["Services"] * 4) * 4,
    "Region": ["North America"] * 12 + ["Europe"] * 12 + ["APAC"] * 12 + ["LATAM"] * 12,
    "Revenue": [
        # Software: NA, EU, APAC, LATAM x 4 quarters
        50, 55, 58, 62,  40, 42, 45, 48,  30, 33, 37, 41,
        # Hardware
        35, 33, 31, 30,  25, 24, 23, 22,  20, 21, 22, 24,
        # Services
        20, 24, 28, 33,  15, 17, 20, 23,  10, 12, 15, 18,
        # LATAM across all
        8, 9, 10, 12,    5, 5, 6, 7,      4, 5, 6, 8,
    ]
}
df = pd.DataFrame(data)

# The recommended chart: faceted stacked bar
fig = px.bar(
    df,
    x="Quarter",
    y="Revenue",
    color="Region",
    facet_col="Product Line",
    title="Revenue Breakdown by Product Line and Region (Last 4 Quarters)",
    text_auto=".2s",
    color_discrete_sequence=px.colors.qualitative.Set2,
)

fig.update_layout(
    template="plotly_white",
    barmode="stack",
    legend_title="Region",
    yaxis_title="Revenue ($M)",
    font=dict(family="Inter, sans-serif"),
    height=500,
    width=1100,
)

# Clean facet labels (remove "Product Line=" prefix)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

# Polish hover
fig.update_traces(
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Revenue: $%{y:.1f}M<br>"
        "<extra>%{fullData.name}</extra>"
    )
)

fig.show()

# Export options:
# fig.write_html("revenue_breakdown.html", include_plotlyjs="cdn")
# fig.write_image("revenue_breakdown.png", width=1100, height=500, scale=2)  # requires kaleido
```

---

## Optional Enhancement: Add a Summary Row

If you also want to see the company-wide total alongside the per-product-line breakdown, create a subplot layout with a full-width stacked bar on top (all product lines as colors) and the faceted regional breakdown below. This provides the macro/micro reading pattern Tufte recommends -- the top chart answers "which product lines drive total revenue?" and the bottom panels answer "which regions drive each product line?"

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Top chart: total revenue by product line per quarter
totals = df.groupby(["Quarter", "Product Line"])["Revenue"].sum().reset_index()

fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.35, 0.65],
    subplot_titles=["Total Revenue by Product Line", "Regional Breakdown per Product Line"],
    vertical_spacing=0.15,
)

# Top: stacked bar of product lines
for product in df["Product Line"].unique():
    subset = totals[totals["Product Line"] == product]
    fig.add_trace(
        go.Bar(x=subset["Quarter"], y=subset["Revenue"], name=product, legendgroup="product"),
        row=1, col=1,
    )

# Bottom: use a grouped+stacked approach or direct the viewer to the px version above
# For the subplot version, stack regions within each product line
for region in df["Region"].unique():
    subset = df[df["Region"] == region]
    fig.add_trace(
        go.Bar(x=[f"{row['Product Line']}<br>{row['Quarter']}" for _, row in subset.iterrows()],
               y=subset["Revenue"], name=region, legendgroup="region",
               marker_color=dict(zip(df["Region"].unique(),
                                     px.colors.qualitative.Set2)).get(region)),
        row=2, col=1,
    )

fig.update_layout(
    barmode="stack",
    template="plotly_white",
    height=900,
    title="Company Revenue: Product Line and Regional Breakdown",
)
fig.show()
```

For most audiences, the simpler faceted stacked bar (first code block) is the right choice. Add the subplot dashboard only if the executive audience explicitly wants both the product-line totals and the regional drill-down in a single view.

---

## Summary

| Aspect | Recommendation |
|--------|---------------|
| **Chart type** | Stacked bar chart, faceted by product line |
| **X-axis** | Quarter (Q1-Q4) |
| **Y-axis** | Revenue |
| **Color** | Region (qualitative palette, Set2) |
| **Facet** | One panel per product line |
| **Library** | Plotly Express (`px.bar` with `facet_col`) |
| **Why not sunburst/treemap** | Cannot show temporal change; less accurate encoding |
| **Why not grouped bar** | Loses part-to-whole total story |
| **Key anti-patterns to avoid** | 3D, truncated y-axis, >7 colors, rainbow palette |
