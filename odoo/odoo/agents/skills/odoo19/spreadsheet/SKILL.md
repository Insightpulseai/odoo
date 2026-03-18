---
name: spreadsheet
description: Integrated spreadsheet tool with Odoo data sources, pivot tables, lists, charts, and global filters
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# spreadsheet -- Odoo 19.0 Skill Reference

## Overview

Odoo Spreadsheet is a full-featured spreadsheet application integrated with the Odoo database. It allows users to create, manipulate, and visualize data using standard spreadsheet functions plus Odoo-specific functions that retrieve live data. It supports inserting lists, pivot tables, and charts from any Odoo app, global filters, templates, version history, collaborative editing, and conversion to dashboards. The Spreadsheet module is part of Odoo Documents.

## Key Concepts

- **Data Sources**: Connections between a spreadsheet and Odoo models, created when inserting lists, pivot tables, or charts. Data refreshes on open, page reload, or manual refresh.
- **Inserted List**: Data from a list view, using `ODOO.LIST()` and `ODOO.LIST.HEADER()` functions.
- **Inserted Pivot Table**: Data from a pivot view, using `PIVOT.HEADER()` and `PIVOT.VALUE()` functions. Can be converted to dynamic pivot tables.
- **Dynamic Pivot Table**: A converted pivot table that allows adding/removing dimensions and measures directly in the spreadsheet.
- **Inserted Chart**: A graph view chart inserted into a spreadsheet. Certain properties editable; no formula-based manipulation.
- **Global Filters**: Cross-data-source filters that dynamically filter all Odoo data in a spreadsheet/dashboard.
- **Templates**: Reusable spreadsheet blueprints. Managed at Documents > Configuration > Spreadsheet Templates.
- **Version History**: Automatic versioning with named versions, restore, and copy capabilities.
- **Locale (Regional Settings)**: Per-spreadsheet setting affecting separators, date/time formats, and first day of week.
- **Command Palette**: Ctrl+K / Cmd+K to browse and execute spreadsheet commands via keyboard.

## Core Workflows

1. **Create a Spreadsheet**
   1. Open Documents, navigate to desired folder.
   2. Click New > Spreadsheet.
   3. Select Blank spreadsheet or a template.
   4. Click Create.

2. **Insert a List from an Odoo App**
   1. Open the relevant list view in any Odoo app.
   2. Click Actions (gear) > Spreadsheet > Insert list in spreadsheet.
   3. Edit name and number of records.
   4. Select target spreadsheet or Blank spreadsheet.
   5. Click Confirm. List is inserted in a new sheet.

3. **Insert a Pivot Table**
   1. Open the relevant pivot view.
   2. Click "Insert in Spreadsheet."
   3. Edit name, select target spreadsheet.
   4. Click Confirm. Convert to dynamic pivot table for manipulation.

4. **Insert a Chart**
   1. Open the relevant graph view.
   2. Click "Insert in Spreadsheet."
   3. Edit name, select target spreadsheet.
   4. Click Confirm. Chart is placed on the first sheet.

5. **Convert Spreadsheet to Dashboard**
   1. Click File > Add to dashboard.
   2. Enter Dashboard Name, select Dashboard Section.
   3. Configure Access Groups.
   4. Click Create. The spreadsheet moves to Dashboards app.

6. **Upload an External File**
   1. In Documents, click New > Upload.
   2. Select `.xlsx` or `.csv` file.
   3. Click on the uploaded file, then "Open with Odoo Spreadsheet."

## Technical Reference

- **Key Functions**:
  - `ODOO.LIST(list_id, index, field_name)` -- retrieve list cell value
  - `ODOO.LIST.HEADER(list_id, field_name)` -- retrieve list column header
  - `PIVOT.VALUE(pivot_id, measure_name, [domain_field_name, ...], [domain_value, ...])` -- retrieve pivot cell value
  - `PIVOT.HEADER(pivot_id, [domain_field_name, ...], [domain_value, ...])` -- retrieve pivot header
  - Financial functions: Odoo-specific functions for account IDs, credits/debits, tax year dates
- **Data Source Properties**: Accessible via Data menu. Each source has Model, Domain, Columns/Rows, Measures, Sorting.
- **List Properties**: List ID, Name, Model, Columns, Domain, Sorting.
- **Pivot Properties**: Pivot ID, Name, Model, Columns, Rows, Measures, Domain.
- **File Menu Actions**: Make a copy, Share (with Freeze and share option), Download (.xlsx), Print, Save as template, Move to trash, Add to dashboard, See version history, Settings (locale).
- **Template Management**: Documents > Configuration > Spreadsheet Templates. Actions: Make a copy, Edit, Delete.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Spreadsheets now serve as the foundation for Odoo Dashboards.
- Dynamic pivot tables allow in-spreadsheet dimension/measure manipulation.
- Global filters work across all data sources in a spreadsheet, including when used as dashboards.
- Version history supports named versions and restore.
- Locale managed at spreadsheet level (not user level) for consistency.

## Common Pitfalls

- Downloading as `.xlsx` converts all Odoo-specific formulas to static values at the moment of download.
- Inserted lists do not auto-expand for new records; extra rows must be added manually or anticipated at insert time.
- Deleting an inserted list/pivot from the sheet does not delete the underlying data source; it must be deleted separately via properties.
- Deleting a chart does delete the underlying data source.
- After converting a spreadsheet to a dashboard, the spreadsheet is removed from Documents and can only be edited via Dashboards.
