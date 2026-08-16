# Perception Science — The Theoretical Foundation

## Table of Contents
1. [Cleveland & McGill's Perceptual Hierarchy](#cleveland--mcgills-perceptual-hierarchy)
2. [Tufte's Principles of Graphical Excellence](#tuftes-principles-of-graphical-excellence)
3. [Pre-Attentive Processing](#pre-attentive-processing)
4. [Color Perception and Theory](#color-perception-and-theory)
5. [Why Specific Charts Work (or Don't)](#why-specific-charts-work-or-dont)
6. [Gestalt Principles in Visualization](#gestalt-principles-in-visualization)

---

## Cleveland & McGill's Perceptual Hierarchy

In 1984, William Cleveland and Robert McGill published groundbreaking research ranking how accurately humans decode different visual encodings. Their experiments showed that perception accuracy follows this hierarchy (most accurate first):

1. **Position on a common scale** (scatter plot, dot plot)
2. **Position on non-aligned scales** (small multiples with different baselines)
3. **Length** (bar chart)
4. **Direction/Angle** (pie chart, slope graph)
5. **Area** (bubble chart, treemap)
6. **Volume** (3D charts — avoid)
7. **Curvature** (rarely used)
8. **Color saturation / density** (heatmap, choropleth)

### What this means in practice

| Encoding | Accuracy | Use when | Example |
|----------|----------|----------|---------|
| Position on common scale | ~1-2% error | Precise comparison needed | Scatter plot comparing two metrics |
| Length on common baseline | ~2-5% error | Comparing magnitudes | Bar chart of sales by category |
| Angle | ~5-15% error | Rough proportions only | Pie chart (2-3 slices max) |
| Area | ~10-25% error | Approximate magnitude | Bubble chart, treemap |
| Color saturation | ~15-30% error | Patterns and trends, not precise values | Heatmap of correlations |

### The bar vs pie experiment
Cleveland & McGill asked subjects to estimate the ratio of a smaller value to a larger value. With **bar charts** (length encoding), average error was about 1.5%. With **pie charts** (angle encoding), average error was about 3.5% — more than double. This isn't a matter of taste; it's measured human perception.

### Why this matters for chart selection
When choosing between chart types, consider which perceptual channel they use:
- **Need precise comparison?** → Use position or length (bar, dot, scatter)
- **Need pattern/trend detection?** → Color and position work well (heatmap, line chart)
- **Need rough overview?** → Area and color are acceptable (treemap, choropleth)

---

## Tufte's Principles of Graphical Excellence

Edward Tufte's "The Visual Display of Quantitative Information" (1983) established foundational principles:

### The Data-Ink Ratio
```
Data-Ink Ratio = (Ink used to display data) / (Total ink used in the graphic)
```

**Goal**: Maximize this ratio. Every non-data element (gridlines, borders, decorative fills, 3D effects) reduces it.

**Practical application**:
- Remove or lighten gridlines (use `template="plotly_white"`)
- Remove chart borders and unnecessary axis lines
- Remove redundant labels (if the axis title says "Revenue ($M)", don't also label each bar)
- Remove backgrounds and fills that don't encode data

**The erasing principle**: For every element in your chart, ask: "Would removing this reduce the information conveyed?" If no, remove it.

### Lie Factor
```
Lie Factor = (Size of effect shown in graphic) / (Size of effect in data)
```

A lie factor of 1.0 is truthful. Common violations:
- **Truncated y-axis on bar charts**: If bars start at 95 instead of 0, a 5% difference looks like a 500% difference. Lie factor: ~100x.
- **Area scaling**: Doubling a circle's radius quadruples its area. If the data doubled, the visual impression quadrupled. Lie factor: 2x.
- **3D perspective**: Bars in the back appear smaller due to perspective, even if they represent equal values.

**Important distinction**: Truncating the y-axis on a **line chart** is acceptable because lines encode position, not length. A bar chart at 95-100 lies; a line chart at 95-100 is just zoomed in.

### Chartjunk
Decorative elements that don't convey data. Includes:
- 3D effects (perspective, shadows, gradients)
- Decorative illustrations
- Moiré patterns from dense hatching
- Heavy gridlines that compete with data

Tufte's stance is absolute: remove all of it. In practice, minimal aesthetic elements (subtle colors, clean typography) aid comprehension by reducing cognitive friction.

### Small Multiples
"At the heart of quantitative reasoning is a single question: Compared to what?"

Small multiples (faceting) show the same chart structure repeated for different subsets of data. They leverage the eye's ability to detect differences across identical templates. This is almost always better than cramming multiple categories into one chart with a complex legend.

**When to facet**: More than 5-7 series on one chart, or when the individual patterns matter as much as the comparison.

### Micro/macro readings
Good visualizations work at multiple levels: a macro view reveals the overall pattern (trend, distribution shape), while zooming in reveals micro detail (individual data points, exact values). Interactive charts excel at this — hover for micro, step back for macro.

---

## Pre-Attentive Processing

Pre-attentive visual features are processed by the brain in under 250 milliseconds — before conscious attention. Leveraging these features lets viewers perceive patterns instantly.

### Pre-attentive features (effective for encoding)

| Feature | Use for | Example |
|---------|---------|---------|
| **Color hue** | Categorical distinction | Different colored lines per group |
| **Color intensity** | Magnitude | Heatmap darkness = higher value |
| **Size** | Magnitude (imprecise) | Bubble chart point size |
| **Orientation** | Direction, categorical | Arrows on a map |
| **Position** | Precise comparison | Point on a scatter plot |
| **Shape** | Categorical (max 5-6) | Different markers per group |
| **Motion** | Change, attention-grabbing | Animated transitions |

### Key limits

- **Color hue**: Max ~7 distinguishable categories. Beyond that, viewers can't reliably map colors to legend entries.
- **Shape**: Max ~5-6 marker shapes before they blur together.
- **Size**: Humans perceive area, not radius. Doubling the data value should double the area (quadratic radius scaling). Even then, area discrimination is imprecise.

### The pop-out effect
A single red dot in a field of blue dots "pops out" — you don't need to search for it. This works because color hue is pre-attentive. But a red square among red circles doesn't pop out as strongly (shape is less salient than color).

**Application**: Use color to highlight the one data point you want the audience to notice. Use grey for everything else. This is the "highlight and grey-out" pattern — incredibly effective for storytelling.

### Interference effects
Combining too many pre-attentive channels degrades all of them. A chart where points vary by color AND shape AND size simultaneously is harder to process than three separate charts each using one channel.

**Rule of thumb**: Encode the most important variable with the strongest pre-attentive feature (position or color), and limit total encoding channels to 2-3 per chart.

---

## Color Perception and Theory

### Perceptual uniformity
A colormap is "perceptually uniform" when equal steps in data correspond to equal steps in perceived color difference. This matters because:
- With a uniform scale (Viridis), a value of 50 looks halfway between 0 and 100
- With a non-uniform scale (jet/rainbow), the yellow band creates a perceptual "cliff" — values near yellow appear to have a discontinuity that doesn't exist in the data

### Why Viridis?
Viridis was designed by Stéfan van der Walt and Nathaniel Smith (2015) to be:
1. **Perceptually uniform** — equal data steps = equal perceived steps
2. **Colorblind-safe** — works for all forms of color vision deficiency (~8% of males)
3. **Grayscale-preserving** — prints correctly in black and white
4. **Perceptually ordered** — lighter = higher, intuitively

No other mainstream colormap satisfies all four. Jet/rainbow fails #1, #2, and #3.

### Color scale selection guide

| Data type | Scale type | Recommended | Why |
|-----------|-----------|-------------|-----|
| Continuous magnitude (0 to max) | Sequential | Viridis, Plasma, Inferno | Perceptually uniform |
| Deviation from center (e.g., profit/loss) | Diverging | RdBu, BrBG | Two hues diverge from neutral center |
| Categorical (unordered groups) | Qualitative | Set2, Safe, Plotly | Maximum distinguishability |
| Binary (yes/no, true/false) | Two-color | Blue/Orange, Teal/Coral | High contrast pair |
| Correlation (-1 to +1) | Diverging | RdBu, centered at 0 | Red = negative, Blue = positive |
| Temperature / heat | Sequential | YlOrRd, Inferno | Cultural association |

### Diverging scale centering
For diverging scales, the midpoint (white/light) MUST align with the meaningful zero:
```python
# Correlation matrix — center at 0
px.imshow(corr_matrix, color_continuous_scale="RdBu",
          color_continuous_midpoint=0)

# Profit/loss — center at 0
px.bar(df, color="profit", color_continuous_scale="RdYlGn",
       color_continuous_midpoint=0)
```

### Colorblind considerations
- ~8% of males and ~0.5% of females have some form of color vision deficiency
- Most common: red-green (deuteranopia/protanopia)
- **Safe combinations**: Blue/Orange, Blue/Red (differ in luminance), Purple/Green
- **Unsafe combinations**: Red/Green (the classic), Green/Brown, Blue/Purple (for some types)
- **Test**: Use https://www.color-blindness.com/coblis-color-blindness-simulator/ to verify

### The "highlight and grey" pattern
Instead of using 12 colors for 12 categories:
```python
colors = ['lightgrey'] * len(df)
colors[important_index] = 'red'
fig = px.bar(df, color=colors)
```
This leverages pre-attentive pop-out: the one colored element instantly draws attention.

---

## Why Specific Charts Work (or Don't)

### Bar charts work because...
They encode values as lengths on a common baseline. Length is the 3rd most accurate perceptual channel (after position on common/non-aligned scales). The common baseline is crucial — without it (e.g., stacked segments above the first), comparison accuracy drops significantly.

**Implication**: In a stacked bar chart, only the bottom segment (touching the baseline) can be compared accurately. For precise comparison of all segments, use grouped bars.

### Pie charts fail because...
They encode values as angles, which is 4th in the perceptual hierarchy. Humans struggle to compare non-adjacent slices. Research shows that even trained analysts make significantly larger errors with pie charts than with bar charts for the same data. The only saving grace: when you have 2-3 slices, the comparison is coarse enough that angular imprecision doesn't matter.

### Line charts work for time because...
Lines imply connection and continuity — exactly what temporal data has. The brain naturally follows lines and perceives trends (slopes) pre-attentively. When there's no temporal or ordered relationship, lines mislead by implying a connection that doesn't exist.

### Heatmaps work for patterns because...
They leverage color saturation to reveal structure in matrices. While individual value reading is imprecise (color is low in the hierarchy), pattern detection across the matrix is excellent — clusters, gradients, outliers all pop out. This is why heatmaps are great for correlation matrices (spot groups of correlated variables) but poor for precise value reading.

### Scatter plots work for relationships because...
They encode both variables as position (the most accurate channel). Patterns like correlation, clusters, outliers, and non-linearity are all visible simultaneously. Adding color (3rd variable) and size (4th variable) creates a multi-dimensional view — but each additional encoding is less precise than the primary position encoding.

---

## Gestalt Principles in Visualization

The Gestalt principles describe how humans perceive visual groups and patterns. They operate automatically and subconsciously.

### Proximity
Objects close together are perceived as a group. Use spatial proximity (margins, padding) to create visual groups in dashboards. Related charts should be close; unrelated charts should have visible separation.

### Similarity
Objects that look similar (same color, shape, size) are perceived as related. This is why using consistent color encoding across a dashboard matters — if "Revenue" is blue in chart 1, it should be blue in chart 2.

### Continuity
The eye follows continuous lines and curves. This is why line charts work — the eye naturally traces the trend. Discontinuities (gaps, sudden changes) draw attention, which is useful for highlighting events or anomalies.

### Enclosure
Elements enclosed by a boundary are perceived as a group. Use subtle backgrounds or borders to group related elements in dashboards. Don't make the boundary too strong — it becomes chartjunk.

### Connection
Elements connected by a line are perceived as related. This is why connected scatter plots (adding lines between sequential points) imply ordering, while regular scatter plots don't.

### Figure/Ground
The eye separates visual input into foreground (the data) and background (the axes, gridlines). Keep the background subdued (light gridlines, minimal borders) so the data dominates. This is Tufte's data-ink ratio expressed in perceptual terms.
