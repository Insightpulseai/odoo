---
name: reporting
description: Analyze data using graph views (bar, line, pie) and pivot tables with measures, grouping, and comparisons.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# reporting — Odoo 19.0 Skill Reference

## Overview

Odoo's reporting framework provides two generic analytical views — **graph** and **pivot** — available under the Reporting menu of most applications. These views enable users to visualize records using bar charts, line charts, and pie charts, or to aggregate and cross-tabulate data in pivot tables. Users select measures (numerical fields), apply groupings, and optionally compare time periods. Sales managers, accountants, and operations analysts use these views for trend analysis, KPI tracking, and ad-hoc data exploration.

## Key Concepts

- **Graph view**: Visual representation of data as bar, line, or pie charts. Accessed via the graph view button in the top-right corner.
- **Pivot view**: Cross-tabulation table for aggregating data along row and column dimensions. Accessed via the pivot view button.
- **Measure**: A numerical field (integer, decimal, monetary) whose values are aggregated. The **Count** measure counts total filtered records.
- **Group By**: Categorizes data by a dimension (e.g., Product Category, Salesperson, Date > Month). Multiple groups can be nested.
- **Stacked charts**: For bar and line charts with 2+ groups, values stack on top of each other instead of side-by-side.
- **Cumulative line**: Line chart option that sums values over time, showing growth trends.
- **Comparison**: Available on certain reports; compares selected time period vs. Previous Period or Previous Year.
- **Flip axis**: Pivot view button that swaps row and column groups.

## Core Workflows

### 1. View a report as a graph

1. Navigate to an app's Reporting menu.
2. Click the **graph view** button (top-right).
3. Select chart type: Bar, Line, or Pie.
4. Click **Measures** to select the metric to display.
5. Use **Group By** to categorize data by dimension.

### 2. View a report as a pivot table

1. Navigate to an app's Reporting menu.
2. Click the **pivot view** button (top-right).
3. Click **Measures** to select one or more metrics.
4. Click the **+** button next to **Total** (rows or columns) to add preconfigured groups.
5. Add subgroups by clicking **+** on newly created group headers.
6. Use the flip axis button to swap rows and columns.

### 3. Enable stacked or cumulative display

1. In a bar or line chart with 2+ groups, toggle the **Stacked** option.
2. In a line chart, toggle the **Cumulative** option to sum values over time.

### 4. Compare time periods

1. In the search bar drop-down, select a time period filter (e.g., Order Date > Q2).
2. In the **Comparison** section, select **Previous Period** or **Previous Year**.
3. The chart or pivot displays side-by-side data for both periods.

### 5. Download pivot data

1. Configure the pivot view with desired measures and groups.
2. Click the download button to export as `.xlsx`.

## Technical Reference

### Views

| View | XML ID Pattern | Purpose |
|------|---------------|---------|
| Graph | `*.view_*_graph` | Chart visualization |
| Pivot | `*.view_*_pivot` | Cross-tabulation |

### Measure Constraints

- Only numerical fields are available as measures: `integer`, `float`, `monetary`.
- **Count** is always available (counts records, not a field).
- Pivot views support multiple simultaneous measures; graph views support one.

### Comparison Behavior by View

| View | Display |
|------|---------|
| Bar chart | Two bars side-by-side per time unit (left = selected, right = previous) |
| Line chart | Two lines (one per period) |
| Pie chart | Large circle (selected) with smaller circle inside (previous) |
| Pivot | Each column split into two sub-columns |

### Sorting (Pivot)

- Click a measure's label header to toggle ascending/descending sort.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Comparison requires time filter**: The Comparison section only appears in the search bar when a time period filter is already selected.
- **Comparison view limitations**: Some reports only support Comparison in Pie Chart or Pivot view. Selecting Comparison in other views may have no visible effect.
- **Group By order matters**: The first group applied is the main cluster; subsequent groups subdivide it. Reordering changes the hierarchy.
- **Default grouping**: Reports often default to Date > Month. Remove or replace this grouping for non-time-series analysis.
