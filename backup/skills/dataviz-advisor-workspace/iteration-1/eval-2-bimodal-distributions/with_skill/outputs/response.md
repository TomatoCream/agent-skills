# Recommendation: Violin Plot

## Why violin, not box plot or histogram?

This is a **distribution** question -- "How is my data spread?" -- with **2-5 groups to compare** and a critical detail: **some endpoints have bimodal distributions**.

The violin plot is the single best chart here because:

1. **It reveals bimodality that box plots hide.** A bimodal distribution and a unimodal distribution with the same median and IQR produce nearly identical box plots. The box plot compresses all shape information into five summary statistics (min, Q1, median, Q3, max), so two distinct peaks are invisible. The violin plot shows the full density curve, making a second mode immediately obvious as a visible bulge.

2. **It enables side-by-side comparison across groups.** With 3 endpoints, you get 3 violins on a shared y-axis, making it easy to compare both the central tendency and the full distributional shape across endpoints. This leverages position on a common scale -- the most accurate perceptual channel per Cleveland & McGill (1984).

3. **Your sample size (n=10,000 per group) is in the sweet spot.** The decision tree marks n=200-5K as "Excellent" for violins, and n=5K-50K as "Good." At 10,000 requests per endpoint, kernel density estimation produces a smooth, reliable shape without noise.

## Why not the alternatives?

| Alternative | Verdict | Reason |
|---|---|---|
| **Box plot** | Reject | Hides bimodality entirely -- the whole point of this analysis. Two peaks collapse into one box. |
| **Histogram** | Second choice | Can show bimodality, but comparing 3 overlapping histograms is cluttered. You would need faceted small multiples, which makes direct shape comparison harder since the distributions are no longer aligned on a common axis. |
| **Ridgeline** | Overkill | Designed for 6-20 distributions. With only 3 endpoints, violins are more compact and easier to read. |
| **ECDF** | Viable complement | Shows exact percentiles and overlays cleanly, but bimodality appears as a subtle inflection rather than a visible second peak. Less intuitive for spotting modes. |
| **Strip/jitter** | Reject | Designed for small datasets (n < 200). At 10,000 points per group, it becomes an unreadable mass of dots. |

## Recommended configuration

Add `box=True` inside each violin to get the best of both worlds: the full density shape plus the box plot's summary statistics (median, quartiles). Show outlier points to flag extreme response times.

```python
import plotly.express as px

fig = px.violin(
    df,
    x="endpoint",
    y="response_time",
    color="endpoint",
    box=True,              # Overlay box plot inside the violin
    points="outliers",     # Show only outlier points to avoid clutter at n=10K
    title="Response Time Distribution by Endpoint",
    labels={"response_time": "Response Time (ms)", "endpoint": "API Endpoint"},
)
fig.update_layout(
    template="plotly_white",
    showlegend=False,       # Color + x-axis label are redundant; drop the legend
)
fig.show()
```

## Anti-patterns to avoid

- **Do not use a box plot as a "simpler" alternative.** Simplicity that hides the key insight (bimodality) is not simplicity -- it is misinformation.
- **Do not overlay 3 histograms on one axis.** Even with transparency, overlapping bins obscure each other. If you want histograms, facet them into small multiples with a shared y-axis scale.
- **Do not truncate the y-axis.** Violins encode density as width, but the y-axis shows the actual response time values. Truncating would hide the tails where slow outliers live.

## Optional enhancement: add a median annotation

For presentations, annotate the median response time directly on each violin so readers do not need to estimate it from the embedded box:

```python
for endpoint in df["endpoint"].unique():
    median_val = df[df["endpoint"] == endpoint]["response_time"].median()
    fig.add_annotation(
        x=endpoint,
        y=median_val,
        text=f"{median_val:.0f}ms",
        showarrow=False,
        xshift=40,
        font=dict(size=11, color="#333"),
    )
```

## Audience note

If the audience is **executives** who may not be familiar with violin plots, consider adding a one-line subtitle: *"Wider sections indicate more requests at that response time."* For a **data science** audience, the violin is immediately understood and no explanation is needed.
