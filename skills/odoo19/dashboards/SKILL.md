---
name: dashboards
description: Interactive dashboard app built on Odoo Spreadsheet for visualizing real-time business metrics
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# dashboards -- Odoo 19.0 Skill Reference

## Overview

Odoo Dashboards provides interactive, real-time dashboards built on Odoo Spreadsheet. Dashboards centralize data from various Odoo sources into tables and charts, allowing users to monitor business performance, filter data with global filters, drill down to underlying records, and share snapshots. Standard pre-configured dashboards are available per installed app, and custom dashboards can be built from scratch or by customizing existing ones. A separate "My Dashboard" feature allows pinning frequently used Odoo views.

## Key Concepts

- **Dashboard**: A spreadsheet converted for display in the Dashboards app. The first sheet serves as the front end.
- **Standard Dashboards**: Pre-configured dashboards installed per app (e.g., CRM, Sales, Warehouse). Reinstalled on version upgrades.
- **Dashboard Sections**: Organizational groups for dashboards in the left panel. Configurable via Configuration > Dashboards.
- **Global Filters**: Search bar filters that apply across all data sources in a dashboard. Include date, text, and relation filters.
- **Data Sources**: Connections to Odoo models via inserted lists, pivot tables, and charts. Visible in the Data menu.
- **My Dashboard**: A personal dashboard (not spreadsheet-based) where users pin frequently consulted Odoo views (list, kanban, pivot, graph, calendar, cohort, gantt, map).
- **Access Rights**: View access managed by user groups per dashboard. `Dashboards / Admin` required for customization/configuration. Data visibility respects underlying model permissions.
- **Dashboard Snapshot**: A frozen version shareable via link with users who lack direct access.

## Core Workflows

1. **View and Interact with a Dashboard**
   1. Open the Dashboards app.
   2. Select a dashboard from the left panel.
   3. Use global filters in the search bar to narrow data.
   4. Click table values or chart data points to drill down to underlying records.
   5. Click chart/table titles to open the source view.

2. **Build a Custom Dashboard**
   1. Prepare data: identify questions, find relevant Odoo views, refine filters/fields.
   2. Insert lists, pivot tables, and/or charts into a spreadsheet (from each app's view).
   3. Manipulate data with formulas and Odoo-specific functions.
   4. Design the first sheet with clear headings, charts, tables, clickable links.
   5. Add global filters for user-driven filtering.
   6. Convert: File > Add to dashboard. Set name, section, access groups.

3. **Customize an Existing Dashboard**
   1. Go to Dashboards > Configuration > Dashboards.
   2. Open the relevant section, click Edit on the dashboard line.
   3. For standard dashboards: duplicate first (File > Make a copy), then edit the copy.
   4. Modify tables, charts, global filters, clickable links as needed.

4. **Manage Dashboard Access**
   1. Go to Configuration > Dashboards.
   2. Open the relevant section.
   3. On the dashboard line, add/remove user Groups.
   4. Optionally restrict by Company in multi-company setups.

5. **Add a View to My Dashboard**
   1. Open any Odoo view (list, kanban, pivot, graph, etc.).
   2. Click Actions (gear) > Dashboard.
   3. Rename if desired, click Add.
   4. Refresh the page. View appears as a widget in My Dashboard.

6. **Share a Dashboard Snapshot**
   1. Open the dashboard.
   2. Click Share (top-right).
   3. Click the copy icon to copy the shareable link.

## Technical Reference

- **Key Models**: `spreadsheet.dashboard`, `spreadsheet.dashboard.group` (sections)
- **Configuration Path**: Dashboards > Configuration > Dashboards. Manage sections, dashboard order, groups, companies, publish/unpublish.
- **Access Rights**:
  - Viewing: Controlled by user groups assigned to each dashboard. `Dashboards / Admin` sees all.
  - Customizing/Building: Requires `Dashboards / Admin`. Building also requires `Documents / User`.
  - Data visibility: Based on user's model-level permissions and record rules.
- **Dashboard Actions**: Reorder sections/dashboards (drag), duplicate sections, delete sections, create sections, edit names, add spreadsheets, unpublish, edit underlying spreadsheet.
- **Chart Interactions**: Expand to full screen, copy as image, download, adjust time granularity, zoom/scroll time-series charts.
- **My Dashboard**: Not spreadsheet-based. Supports layout customization (multi-column), widget collapse/expand, drag-and-drop reorder, remove widgets. Views retain interactivity (sorting, measure changes, chart type changes, record drill-down).

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Dashboards app now built entirely on Odoo Spreadsheet as the foundation.
- Standard dashboards reinstalled at each version upgrade; customizations on originals are lost.
- Time-series charts support granularity adjustment and zoom/scroll in full-screen mode.
- Global filters combine with data source domains when loading data.
- My Dashboard retains dynamic view features (sorting, measure changes, chart type switching).

## Common Pitfalls

- Customizing a standard dashboard directly means changes are lost on version upgrade. Always duplicate first.
- A user may have dashboard access but see incomplete data due to insufficient model-level permissions.
- After converting a spreadsheet to a dashboard, it is removed from Documents and can only be edited via Dashboards.
- Deleting a dashboard element does not auto-delete its data source; unused data sources show a warning in the Data menu.
- Standard dashboard sections cannot be deleted; only custom sections can.
