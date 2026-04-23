# Executive Dashboard Recommendation for Quarterly Review

## Understanding the Context

You have 50,000 transaction rows with four dimensions: **date**, **amount**, **category** (12 values), **region** (4 values). Your audience is a VP at a quarterly review -- this means the dashboard needs to be high-level, insight-driven, and polished. Executives want answers, not raw data.

---

## Recommended Dashboard Structure

Build a **single-page interactive dashboard** with 5-6 linked visualizations. Here is what to include and why.

### 1. KPI Summary Bar (Top of Dashboard)

Place 4-5 large-number cards across the top:

- **Total Revenue** (sum of amount)
- **Transaction Count** (50,000 or filtered subset)
- **Average Transaction Value**
- **Quarter-over-Quarter Growth %** (if prior quarter data is available)
- **Top Performing Region** (by total amount)

**Why:** Executives look at the top of the page first. These numbers answer "how did we do?" in under 3 seconds.

### 2. Revenue Trend Over Time (Line Chart)

- X-axis: date, aggregated to **weekly** or **monthly** buckets
- Y-axis: total amount
- Optionally overlay lines by region (4 lines) or show a single aggregate line with a trend/moving average

**Why:** The first question in any quarterly review is "what's the trajectory?" A time-series line chart answers this immediately and reveals seasonality or anomalies.

### 3. Revenue by Category (Horizontal Bar Chart)

- Y-axis: 12 categories, sorted descending by total amount
- X-axis: total amount
- Color-code bars or add data labels with percentage of total

**Why:** With 12 categories, a horizontal bar chart is more readable than a pie chart. Sorting by value lets the VP instantly see which categories drive the business and which are underperforming.

### 4. Revenue by Region (Choropleth Map or Donut Chart)

- If the 4 regions are geographic, use a **simple map** or **filled region chart**
- If regions are abstract (e.g., "Enterprise", "SMB"), use a **donut chart** or **stacked bar**
- Show both absolute revenue and percentage share

**Why:** Regional performance is a staple of executive reviews. With only 4 regions, a donut chart is acceptable here (unlike with 12 categories). A map adds visual appeal if regions are geographic.

### 5. Category x Region Heatmap (Matrix/Heatmap)

- Rows: 12 categories
- Columns: 4 regions
- Cell color intensity: total amount (or average transaction value)

**Why:** This is the cross-dimensional view that reveals where specific opportunities or problems exist -- e.g., "Category X is underperforming specifically in Region Y." This is the kind of insight that drives action items in a quarterly review.

### 6. Distribution of Transaction Amounts (Histogram or Box Plot)

- Show distribution of individual transaction amounts
- Optionally segment by category or region using box plots

**Why:** Averages can hide important patterns. If your transactions range from $5 to $50,000, the VP should know. This also surfaces outliers that might skew the headline numbers.

---

## Interactivity and Filters

Add the following global filters that cross-filter all charts:

- **Date range selector** (default to the current quarter)
- **Region dropdown** (multi-select)
- **Category dropdown** (multi-select)

Clicking on a region in the map/donut should filter all other charts. Same for clicking a category bar.

---

## Tool Recommendation

| Tool | Best For | Effort |
|------|----------|--------|
| **Tableau / Power BI** | Polished, interactive, easy to share with executives | Low-Medium |
| **Python (Plotly Dash)** | Full customization, version-controlled, reproducible | Medium-High |
| **Python (Streamlit)** | Quick prototype, good interactivity, easy deployment | Medium |
| **Looker / Metabase** | If data lives in a database and you want self-service | Medium |
| **Google Sheets / Excel** | If the VP specifically wants a spreadsheet they can click around in | Low |

**My recommendation:** If this is a one-time quarterly presentation, use **Tableau** or **Power BI** -- they produce executive-grade visuals with minimal code. If this will be recurring and you want automation, build it in **Plotly Dash** or **Streamlit** so you can re-run it every quarter with fresh data.

---

## Data Preparation Tips

Before building, prepare your data:

1. **Parse dates** and extract `year`, `quarter`, `month`, `week` columns for flexible time aggregation.
2. **Validate amounts** -- check for nulls, negatives, and outliers. Decide how to handle them before the VP asks.
3. **Standardize category and region names** -- inconsistent casing or spelling will split your aggregations.
4. **Pre-compute summary tables**: totals by category, by region, by category-region, and by time period. This speeds up dashboard rendering on 50K rows.

---

## Presentation Tips for the VP Audience

- **Lead with the story, not the chart.** Title each chart with an insight, not a description. Use "Revenue grew 12% QoQ driven by Category A" instead of "Revenue by Quarter."
- **Use consistent colors.** Assign a fixed color to each region across all charts so the VP can track regions visually.
- **Limit to one page.** If it does not fit on one screen, it is too much. Use drill-down interactions instead of more pages.
- **Prepare for "why" questions.** Have a second detail tab or backup slides that break down any metric the VP might question.
- **Include a brief written summary** (3-5 bullet points) at the top or in a sidebar summarizing the key takeaways.

---

## Summary

Build a single-page dashboard with: KPI cards at the top, a revenue time-series, category bar chart, region breakdown, a category-by-region heatmap, and a transaction distribution chart. Add cross-filtering by date, region, and category. Use Tableau/Power BI for executive polish, or Plotly Dash/Streamlit for automation. Lead every chart with an insight, not just a label.
