# Finance PPM Seed Data Documentation

## Overview

This directory contains seed data for the **TBWA SMP Month-End Closing & Tax Filing 2025–2026** project, structured as a Work Breakdown Structure (WBS) with 4 phases and 29 tasks.

## Files

- **`ppm_seed_finance_wbs_2025_2026.xml`** - Odoo XML data file (primary seed data)
- **`ppm_seed_schema.json`** - JSON Schema documentation for data structure
- **`README.md`** - This file

## Data Structure

### Project Hierarchy

```
Project: TBWA SMP – Month-End Closing & Tax Filing 2025–2026
├── Phase 1: November 2025 Closing (5 tasks)
├── Phase 2: December 2025 & Year-End Closing (4 tasks)
├── Phase 3: Tax Compliance – Nov & Dec 2025 (4 tasks)
└── Phase 4: 2026 Monthly Closing & Tax Cycle (12 milestones)
```

### Phase Breakdown

#### Phase 1: November 2025 Closing
**Deadline**: 2025-12-05 | **Sequence**: 10

Tasks:
1. **Nov 2025 – GL & Sub-ledger Reconciliation** (2025-11-30)
2. **Nov 2025 – Accruals & Provisions Posting** (2025-12-02)
3. **Nov 2025 – WIP & Revenue Recognition** (2025-12-03)
4. **Nov 2025 – Trial Balance Review & Sign-off** (2025-12-04)
5. **Nov 2025 – Management Reporting Pack** (2025-12-05)

#### Phase 2: December 2025 & Year-End Closing
**Deadline**: 2026-01-15 | **Sequence**: 20

Tasks:
1. **Dec 2025 – Pre-close Reconciliations** (2025-12-29)
2. **Dec 2025 – Final Accruals & Cut-offs** (2026-01-05)
3. **Dec 2025 – Year-End Adjustments & Provisions** (2026-01-08)
4. **Dec 2025 – Audit Pack & Schedules** (2026-01-12)

#### Phase 3: Tax Compliance – Nov & Dec 2025
**Deadline**: 2026-01-20 | **Sequence**: 30

Tasks:
1. **Tax – Nov 2025 1601-C & 0619-E Filing** (2025-12-10)
2. **Tax – Nov 2025 VAT 2550M Filing** (2025-12-20)
3. **Tax – Dec 2025 1601-C & 0619-E Filing** (2026-01-10)
4. **Tax – Dec 2025 VAT 2550M & Annual Reconciliations** (2026-01-20)

#### Phase 4: 2026 Monthly Closing & Tax Cycle
**Deadline**: 2026-12-31 | **Sequence**: 40

Monthly Milestones (12):
1. January 2026 Books Closed (2026-02-05)
2. February 2026 Books Closed (2026-03-05)
3. March 2026 Books Closed (2026-04-05)
4. April 2026 Books Closed (2026-05-05)
5. May 2026 Books Closed (2026-06-05)
6. June 2026 Books Closed (2026-07-05)
7. July 2026 Books Closed (2026-08-05)
8. August 2026 Books Closed (2026-09-05)
9. September 2026 Books Closed (2026-10-05)
10. October 2026 Books Closed (2026-11-05)
11. November 2026 Books Closed (2026-12-05)
12. December 2026 Books & FY 2026 Closed (2027-01-15)

## XML Structure Reference

### Project Record
```xml
<record id="project_finance_ppm_2025_2026" model="project.project">
  <field name="name">TBWA SMP – Month-End Closing &amp; Tax Filing 2025–2026</field>
  <field name="privacy_visibility">followers</field>
</record>
```

### Phase Task Record
```xml
<record id="task_phase_nov_2025_closing" model="project.task">
  <field name="name">Phase: November 2025 Closing</field>
  <field name="project_id" ref="project_finance_ppm_2025_2026"/>
  <field name="date_deadline">2025-12-05</field>
  <field name="sequence">10</field>
  <field name="is_phase" eval="True"/>
</record>
```

### Regular Task Record
```xml
<record id="task_nov25_gl_recon" model="project.task">
  <field name="name">Nov 2025 – GL &amp; Sub-ledger Reconciliation</field>
  <field name="project_id" ref="project_finance_ppm_2025_2026"/>
  <field name="parent_id" ref="task_phase_nov_2025_closing"/>
  <field name="date_deadline">2025-11-30</field>
  <field name="sequence">11</field>
</record>
```

## Field Definitions

| Field Name | Type | Description | Required |
|------------|------|-------------|----------|
| `id` | XML ID | Unique identifier for Odoo record reference | Yes |
| `name` | Char | Task or project name | Yes |
| `project_id` | Many2one | Reference to parent project | Yes (tasks only) |
| `parent_id` | Many2one | Reference to parent phase task | No |
| `date_deadline` | Date | Task deadline date (YYYY-MM-DD) | No |
| `sequence` | Integer | Display order (10, 20, 30...) | No |
| `is_phase` | Boolean | Mark task as phase container | No |

## Odoo 18 CE Compatibility Notes

### Removed Enterprise-Only Fields
The following fields were removed for Community Edition compatibility:

1. **`allow_timesheets`** - Only available in Odoo Enterprise `project_timesheet` module
2. **`planned_hours`** - Only available in Odoo Enterprise `project_forecast` module

### Field Name Migrations
Studio-generated field names were converted to standard Odoo field names:

| Studio Field | Standard Field |
|--------------|---------------|
| `x_is_phase` | `is_phase` |

### View Compatibility
All view references use Odoo 18 standards:
- `<tree>` → `<list>` (view type renamed in Odoo 18)

## Database Schema

### Project Table (`project_project`)
```sql
CREATE TABLE project_project (
  id SERIAL PRIMARY KEY,
  name JSONB,  -- Multi-language support in Odoo 18
  privacy_visibility VARCHAR,
  ...
);
```

### Task Table (`project_task`)
```sql
CREATE TABLE project_task (
  id SERIAL PRIMARY KEY,
  name JSONB,  -- Multi-language support in Odoo 18
  project_id INTEGER REFERENCES project_project(id),
  parent_id INTEGER REFERENCES project_task(id),
  date_deadline DATE,
  sequence INTEGER,
  is_phase BOOLEAN,
  ...
);
```

## Usage Examples

### Load Seed Data (via CLI)
```bash
docker exec odoo_container odoo \
  -d database_name \
  -u omc_finance_ppm \
  --stop-after-init
```

### Query Loaded Data (SQL)
```sql
-- Get project
SELECT id, name::text FROM project_project
WHERE name::text LIKE '%TBWA SMP%';

-- Count tasks and phases
SELECT
  COUNT(*) as total_tasks,
  SUM(CASE WHEN is_phase THEN 1 ELSE 0 END) as phases
FROM project_task;

-- Get tasks by phase
SELECT
  p.name::text as phase_name,
  COUNT(t.id) as task_count
FROM project_task p
LEFT JOIN project_task t ON t.parent_id = p.id
WHERE p.is_phase = true
GROUP BY p.id, p.name;
```

### Regenerate Seed Data

If you need to regenerate seed data with different dates or tasks:

1. Copy `ppm_seed_finance_wbs_2025_2026.xml` to a new file
2. Update XML IDs (must be unique)
3. Modify dates, task names, and sequences
4. Add to `__manifest__.py` data list
5. Upgrade module: `odoo -d db_name -u omc_finance_ppm --stop-after-init`

## Validation

### Pre-Load Validation
```bash
# Validate XML syntax
xmllint --noout addons/omc_finance_ppm/data/ppm_seed_finance_wbs_2025_2026.xml

# Check for Enterprise-only fields (should return empty)
grep -E "allow_timesheets|planned_hours" addons/omc_finance_ppm/data/*.xml
```

### Post-Load Validation
```bash
# Verify record counts
psql -d database_name -c "SELECT COUNT(*) FROM project_task;"
# Expected: 29

psql -d database_name -c "SELECT COUNT(*) FROM project_task WHERE is_phase = true;"
# Expected: 4

psql -d database_name -c "SELECT COUNT(*) FROM project_project;"
# Expected: 1 (or more if other projects exist)
```

## Troubleshooting

### Common Issues

**Issue**: `ValueError: Invalid field 'planned_hours'`
- **Cause**: Enterprise-only field in seed data
- **Fix**: Remove `<field name="planned_hours">` lines from XML

**Issue**: `ParseError: Invalid view type: 'tree'`
- **Cause**: Odoo 18 renamed `tree` to `list`
- **Fix**: Update view XML to use `<list>` instead of `<tree>`

**Issue**: `KeyError: 'project.task'`
- **Cause**: Missing dependency or model not loaded
- **Fix**: Ensure `project` module is in `depends` list in `__manifest__.py`

**Issue**: Project name showing as `{"en_US": "..."}`
- **Cause**: JSONB field in Odoo 18 for multi-language support
- **Fix**: Use `name::text` in SQL queries or access via ORM which handles translation

## Metadata

- **Odoo Version**: 18.0-20251106
- **Module**: omc_finance_ppm v1.0
- **Total Records**: 30 (1 project + 29 tasks)
- **Date Range**: 2025-11-01 to 2027-01-15
- **Last Updated**: 2025-11-28
- **License**: LGPL-3
- **Maintainer**: TBWA SMP Finance Team
