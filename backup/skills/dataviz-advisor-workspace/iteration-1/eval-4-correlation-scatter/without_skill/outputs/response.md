# Visualizing Correlation Between Two Continuous Variables (~200 Data Points)

## Recommended Chart: Scatter Plot

A **scatter plot** is the best choice for examining the relationship between two continuous variables. It lets you visually assess the direction, strength, and form of the association at a glance.

## Why a Scatter Plot Works Best

- **Reveals the relationship pattern**: You can immediately see whether the relationship is positive, negative, linear, curvilinear, or nonexistent.
- **Exposes outliers**: Individual points that deviate from the overall trend are easy to spot.
- **Handles your data size well**: 200 points is an ideal range for scatter plots -- enough to reveal a pattern without excessive overplotting.
- **Shows data distribution**: You can see how the data is spread across both variables, including any clustering or gaps.

## How to Build It

### Axes
- Place the **independent variable** (or the one you consider the predictor) on the **x-axis**.
- Place the **dependent variable** (or outcome) on the **y-axis**.
- If neither variable is clearly independent, the assignment does not matter.

### Enhancing the Plot

1. **Add a trend line**: Overlay a linear regression line (line of best fit) to make the direction and strength of the correlation visually explicit. Include the R-squared value or Pearson correlation coefficient (r) in an annotation or the title.

2. **Add a LOESS/LOWESS smoother**: If you suspect the relationship might not be strictly linear, a locally weighted smoothing curve will reveal curvature without forcing a parametric form.

3. **Marginal distributions** (optional): Adding small histograms or density plots along the x-axis and y-axis margins helps you understand the distribution of each variable individually alongside the bivariate view.

4. **Confidence band**: Show the 95% confidence interval around the trend line to communicate uncertainty in the fitted relationship.

### Formatting Tips
- Use semi-transparent points (`alpha = 0.5`-`0.7`) to handle any mild overplotting at 200 points.
- Use a 1:1 aspect ratio if the scales of both variables are comparable.
- Label axes clearly with variable names and units.

## Example Code (Python with Matplotlib/Seaborn)

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Scatter plot with regression line and confidence band
sns.regplot(x='variable_x', y='variable_y', data=df,
            scatter_kws={'alpha': 0.6, 's': 30},
            line_kws={'color': 'red'})

plt.xlabel('Variable X (units)')
plt.ylabel('Variable Y (units)')
plt.title('Correlation between X and Y (r = 0.XX)')
plt.tight_layout()
plt.show()
```

For marginal distributions alongside the scatter:

```python
sns.jointplot(x='variable_x', y='variable_y', data=df,
              kind='reg', height=7,
              joint_kws={'scatter_kws': {'alpha': 0.6}})
plt.show()
```

## Example Code (R with ggplot2)

```r
library(ggplot2)

ggplot(df, aes(x = variable_x, y = variable_y)) +
  geom_point(alpha = 0.6, size = 2) +
  geom_smooth(method = "lm", se = TRUE, color = "red") +
  labs(x = "Variable X (units)", y = "Variable Y (units)",
       title = "Correlation between X and Y") +
  theme_minimal()
```

## Quantifying the Correlation

Alongside the visualization, compute:

- **Pearson's r**: Measures linear correlation strength and direction (-1 to +1).
- **Spearman's rho**: A rank-based alternative if the relationship is monotonic but not necessarily linear, or if the data contains outliers.
- **p-value**: Assess statistical significance of the correlation.

## Alternatives Considered

| Chart Type | Verdict |
|---|---|
| **Heatmap / 2D density plot** | Better for thousands of points with heavy overplotting. At 200 points, a scatter plot is clearer. |
| **Bubble chart** | Useful if you have a third variable to encode as bubble size, but unnecessary for two variables. |
| **Paired bar chart** | Not appropriate for continuous-continuous relationships. |
| **Line chart** | Only appropriate if one variable is ordered (e.g., time). |

## Summary

For 200 data points and two continuous variables, use a **scatter plot with a regression line and correlation coefficient annotation**. Optionally add marginal density plots (`jointplot` in Seaborn or `ggMarginal` in R) for a richer view of both variables' distributions.
