---
name: export_import_data
description: Export records to CSV/XLSX and import data from files, including relation fields, external IDs, and bulk updates.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# export_import_data — Odoo 19.0 Skill Reference

## Overview

Odoo provides built-in tools to export and import data across any business object. Exports generate CSV or XLSX files from list views with configurable field selection and reusable templates. Imports accept CSV/XLSX files to create or update records, supporting relational fields (many2one, many2many, one2many), External IDs for cross-system migration, and image attachments. This functionality is used during implementation, data migration, bulk corrections, and periodic reporting.

## Key Concepts

- **Export**: Select records in list view > Actions > Export. Generates CSV or XLSX with chosen fields.
- **Import-compatible export**: Checkbox option that limits exported fields to those that can be re-imported, and auto-includes External ID.
- **Export template**: Saved field selections for recurring exports. Named and reusable via drop-down.
- **External ID (ID)**: A unique string identifier per record, critical for updating existing records and linking relational fields across imports. Format: `module.xml_id` or user-defined (e.g., `company_1`).
- **Database ID**: The PostgreSQL auto-increment integer ID. Unique but opaque; use External ID when possible.
- **Import**: Upload CSV/XLSX > map columns to Odoo fields > Test > Import.
- **Relation fields**: Many2one, many2many, and one2many fields that link records across models. Imported via name, Database ID (`Field/Database ID`), or External ID (`Field/External ID`).
- **Many2many import**: Tags/values separated by commas without spaces (e.g., `Manufacturer,Retailer`).
- **One2many import**: Each sub-record on a separate row; parent fields filled only on the first row.
- **Import-compatible update**: Re-importing a file with External ID or Database ID column updates existing records instead of creating duplicates.

## Core Workflows

### 1. Export data from a list view

1. Navigate to the desired model's list view.
2. Select records via checkboxes (or select all).
3. Click **Action** > **Export**.
4. In the Export Data popup:
   - Tick **I want to update data (import-compatible export)** to include External ID and limit to importable fields.
   - Choose format: CSV or XLSX.
   - Add/remove/reorder fields.
   - Optionally save as a named template.
5. Click **Export**.

### 2. Import data from a file

1. Navigate to the target model's list view.
2. Click the **Action** icon > **Import records**.
3. Optionally download the import template (**Import Template for [Model]**).
4. Click **Upload Data File** and select CSV or XLSX.
5. Adjust **Formatting** options (CSV only): separator, text delimiter, date format, thousands separator.
6. Verify column mapping: File Column -> Odoo Field.
7. Click **Test** to validate.
8. Click **Import**.

### 3. Update existing records via import

1. Export the records with **import-compatible export** (includes External ID).
2. Edit the exported file — modify values but **keep External IDs unchanged**.
3. Re-import the file. Odoo matches on External ID and updates instead of creating duplicates.

### 4. Import relational data from another system

1. Assign External IDs to parent records (e.g., `company_1`, `company_2`).
2. Import parent records first (e.g., Companies).
3. In child records file, reference parents via `Related Field/External ID` (e.g., `Related Company/External ID = company_1`).
4. Import child records (e.g., People).

### 5. Import images

1. Add image filenames to the **Image** column in the data file.
2. Upload the data file.
3. Click **Upload your files** under **Files to import** and select image files.
4. Click **Test** then **Import**. Odoo auto-matches filenames.

## Technical Reference

### Import File Formats

| Format | Notes |
|--------|-------|
| CSV | Comma-separated; Formatting options visible during import |
| XLSX | Excel format; no Formatting options shown |
| XLS | Legacy Excel format; supported |

### Column Naming for Relations

| Pattern | Meaning |
|---------|---------|
| `Field Name` | Match by display name |
| `Field Name/Database ID` | Match by PostgreSQL ID |
| `Field Name/External ID` | Match by XML ID / External ID |
| `Field Name/ID` | Synonym for External ID |

### Developer Mode Import Options

| Option | Effect |
|--------|--------|
| Track history during import | Enables chatter subscriptions/notifications (slower) |
| Allow matching with subfields | Uses all subfields for Odoo Field matching |

### Date Format

- Must follow ISO 8601: `YYYY-MM-DD` (e.g., `1981-07-24`).
- CSV imports allow configuring date format in Formatting section.
- XLSX files should use native date cells.

### Menu Paths

- Any list view > **Action** > **Export**
- Any list view > **Action** > **Import records**

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Imports are permanent**: There is no undo. Use `created on` or `last modified` filters to identify imported records.
- **External ID must remain consistent**: Changing or removing an External ID during re-import causes duplicates instead of updates.
- **Timeout on large files**: Very large imports/exports can timeout. Process in smaller batches.
- **Many2many comma format**: Tags must be comma-separated with **no spaces** (e.g., `Tag1,Tag2` not `Tag1, Tag2`).
- **One2many row structure**: Parent data only on the first row; subsequent rows for additional sub-records must leave parent columns empty.
- **Empty vs. missing fields**: An empty value in a CSV cell sets the field to empty; a missing column uses the default value. This distinction matters for clearing existing data.
