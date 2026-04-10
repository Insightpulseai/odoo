# Charts & Data Visualization

## Chart Selection Guide

| Data Type | Recommended Chart | Avoid |
|-----------|-------------------|-------|
| Trend over time | Line / Area | Pie chart |
| Category comparison | Bar (horizontal or vertical) | Pie for >5 categories |
| Part-to-whole | Stacked bar, treemap | Pie for many slices |
| Distribution | Histogram / Box plot | Bar chart |
| Correlation | Scatter plot | Line chart |
| Flow / Process | Sankey / Funnel | Bar chart |
| Geospatial | Choropleth / Bubble map | Table |

## Dashboard Layout Rules

1. **KPI row first** — show key metrics at top
2. **Filters left or top** — keep filter count manageable (< 5 visible)
3. **Definitions and tooltips** — provide context for derived metrics
4. **Consistent time ranges** — all charts on a dashboard should share the same time filter
5. **Data table alternative** — provide table view for accessibility

## Color in Charts

- Use accessible color palettes (distinguishable by colorblind users)
- Limit to 5-7 colors per chart; group remaining as "Other"
- Use sequential palettes for ordered data; categorical for unordered
- Avoid red/green as the only differentiator

## Chart-Specific Rules

| Rule | Do | Don't |
|------|----|----- |
| `chart-type` | Match chart type to data relationship | Use pie for everything |
| `color-guidance` | Use accessible, distinguishable palettes | Rely on color alone |
| `data-table` | Provide table alternative | Only show visual chart |
| `axis-labels` | Label axes clearly with units | Omit axis context |
