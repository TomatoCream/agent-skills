# Recommended Chart: Violin Plot (primary) + Overlaid Strip/Jitter Plot or Ridgeline Plot (alternative)

## Primary Recommendation: Violin Plot

A **violin plot** is the best choice here for several reasons:

1. **Reveals distribution shape.** Unlike box plots, violin plots show the full density profile of each endpoint's response times. This is critical because you explicitly have bimodal distributions -- a box plot would hide the two peaks entirely, collapsing them into a single median and interquartile range.

2. **Side-by-side comparison across endpoints.** Place the three endpoints along the x-axis, with response time on the y-axis. Each violin's width encodes the density of observations at that response time, making it immediately obvious which endpoints are bimodal and where the modes sit.

3. **Handles 10,000 points well.** Violin plots use kernel density estimation, so they summarize large datasets smoothly without overplotting.

### Enhancement: Embed a box plot inside each violin

Most libraries (Seaborn, ggplot2, Plotly) let you overlay a miniature box plot or quartile markers inside the violin. This gives you the best of both worlds: the full distribution shape plus summary statistics (median, IQR).

## Strong Alternative: Ridgeline (Joy) Plot

If you want an even clearer view of the bimodal shapes, a **ridgeline plot** (also called a joy plot) stacks the three density curves vertically with slight overlap. Each endpoint gets its own row with a KDE curve filled in. This layout makes it very easy to compare the shapes and see exactly where the two modes fall for each endpoint.

- Use the y-axis for the three endpoint categories (stacked vertically).
- Use the x-axis for response time.
- Each ridge shows the density curve.

Ridgeline plots are especially effective when the primary goal is comparing distribution shapes rather than precise quantile values.

## What to Avoid

| Chart Type | Why It Falls Short |
|---|---|
| **Box plot** | Hides bimodality entirely. Two very different distributions can produce identical box plots. |
| **Histogram** | Works for a single endpoint, but overlapping histograms for three groups become cluttered and hard to read. Dodged/faceted histograms are acceptable but less compact than violins. |
| **Bar chart of means** | Discards all distributional information. Particularly misleading for bimodal data where the mean may sit in a valley between the two modes. |
| **Raw scatter/strip plot alone** | With 10,000 points per endpoint (30,000 total), overplotting makes it hard to see density differences even with jittering and transparency. |

## Implementation Notes

- **Python (Seaborn):** `sns.violinplot(x="endpoint", y="response_time", data=df, inner="box", cut=0)` -- the `cut=0` parameter prevents the KDE from extending beyond observed data, and `inner="box"` embeds the box plot.
- **Python (Plotly):** `px.violin(df, x="endpoint", y="response_time", box=True, points=False)` for an interactive version.
- **R (ggplot2):** `ggplot(df, aes(x=endpoint, y=response_time)) + geom_violin() + geom_boxplot(width=0.1)`.
- **For ridgeline in R:** `ggridges::geom_density_ridges()`.
- **For ridgeline in Python:** `joypy` library or manual KDE plotting with matplotlib.

## Summary

Use a **violin plot** as your default choice -- it directly exposes bimodality, compares three groups cleanly, and scales well to 10,000 observations per group. If your audience is less familiar with violin plots, a **ridgeline plot** is an equally effective and often more intuitive alternative. Avoid box plots and bar charts, as they will obscure the most important feature of your data: the bimodal shape.
