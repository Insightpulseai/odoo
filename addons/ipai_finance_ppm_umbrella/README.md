# IPAI Finance PPM – TBWA Canonical Umbrella Module

Complete seed data configuration for TBWA Finance Shared Service Center (SSC) operations with BIR compliance and month-end closing workflows.

## Overview

This umbrella module provides **canonical seed data** for the Finance PPM framework, including:

- **8 Employees**: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB (+ JRMO)
- **12 Logframe Entries**: Goal → Outcome → IM1/IM2 → Outputs → Activities
- **144 BIR Schedule Records**: 18 BIR forms × 8 employees (Dec 2025 - Q3 2026)
- **36 Month-End Closing Tasks**: Complete RACI matrix and task dependencies

## Module Structure

```
ipai_finance_ppm_umbrella/
├── __manifest__.py                    # Module configuration
├── __init__.py                        # Python init
├── README.md                          # This file
├── security/
│   └── ir.model.access.csv           # Access rights
├── data/
│   ├── 01_employees.xml              # 8 employee users (38 lines)
│   ├── 02_logframe_complete.xml      # 12 logframe entries (114 lines)
│   ├── 03_bir_schedule.xml           # 144 BIR forms (2,022 lines, 111KB)
│   └── 04_closing_tasks.xml          # 36 closing tasks (330 lines)
└── scripts/
    └── generate_seed_from_excel.py   # Seed data generator
```

## Installation

### Prerequisites

1. **Base Finance PPM Module** installed:
   ```bash
   odoo -d production -i ipai_finance_ppm
   ```

2. **Dependencies**: `project`, `base`

### Install Umbrella Module

```bash
odoo -d production -i ipai_finance_ppm_umbrella
```

### Verify Installation

```sql
-- Check BIR schedule count
SELECT COUNT(*) FROM ipai_finance_bir_schedule;
-- Expected: 144 records

-- Check logframe count
SELECT COUNT(*) FROM ipai_finance_logframe;
-- Expected: 12 records

-- Check closing tasks
SELECT COUNT(*) FROM project_task WHERE finance_logframe_id IS NOT NULL;
-- Expected: 36 records

-- Check employees
SELECT COUNT(*) FROM res_users WHERE login IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb');
-- Expected: 8 users
```

## Seed Data Details

### 1. Employees (8 users)

**Employee Codes**: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

Created as `res.users` with:
- Login credentials (employee code in lowercase)
- Default access rights
- Ready for RACI matrix assignments

### 2. Logframe (12 entries)

**Hierarchical Structure**:

| Level | Code | Description |
|-------|------|-------------|
| Goal | GOAL-001 | 100% Compliant and Timely Month-End Closing and Tax Filing |
| Outcome | OUTCOME-001 | Zero-Penalty Compliance with Timely Financial Reporting |
| IM1 | IM1 | Month-End Closing Processes |
| IM2 | IM2 | Tax Filing Compliance |
| Outputs | OUT-01 to OUT-04 | Task category outputs |
| Activities | ACT-IM1-01 to ACT-IM2-04 | Execution activities |

**Each entry includes**:
- Code and name
- Indicators (measurable outcomes)
- Means of verification
- Assumptions (risk factors)
- Sequence for ordering

### 3. BIR Schedule (144 records)

**18 BIR Forms** × **8 Employees** = **144 Total Records**

#### BIR Forms Included:

| Form Code | Type | Frequency | Count |
|-----------|------|-----------|-------|
| 1601-C / 0619-E | Withholding | Monthly | 12 × 8 = 96 |
| 2550Q | VAT | Quarterly | 4 × 8 = 32 |
| 1601-EQ | Quarterly EWT | Quarterly | 4 × 8 = 32 |
| 1702-RT/EX | Income Tax | Annual | 1 × 8 = 8 |
| 1702Q | Quarterly Income Tax | Quarterly | 1 × 8 = 8 |

#### Each BIR Record Includes:

- **Period Covered**: Month/Quarter/Year
- **Filing Deadline**: Official BIR due date
- **Prep Deadline**: BIR deadline - 4 business days
- **Review Deadline**: BIR deadline - 2 business days
- **Approval Deadline**: BIR deadline - 1 business day

**RACI Assignments** (per Excel):
- **Supervisor**: BOM (Finance Supervisor)
- **Reviewer**: RIM (Senior Finance Manager)
- **Approver**: CKVC (Finance Director)

**Linked to**: Logframe IM2 (Tax Filing Compliance)

**Status Fields**:
- `status`: not_started (default)
- `completion_pct`: 0.0 (default)

### 4. Closing Tasks (36 records)

**Task Categories** (from Excel):
- Payroll & Personnel
- Tax & Provisions
- Rent & Leases
- Accruals & Expenses
- Amortization & Corporate
- Client Billings
- WIP/OOP Management
- VAT & Taxes
- Asset & Lease Entries
- Reclassifications
- AR/AP Aging
- Regional Reporting

#### Each Task Includes:

- **Task Name**: Detailed monthly task description
- **Category**: Task classification
- **Employee Assignment**: Primary responsible employee
- **RACI Matrix**:
  - Preparation: Employee (typically 1 day)
  - Review: Reviewer (typically 0.5 day)
  - Approval: Approver (typically 0.5 day)
- **Logframe Link**: Connected to relevant output/activity

**Linked to**: Finance PPM project (`project_month_end_closing`)

## Regenerating Seed Data

If the Excel source file is updated:

### 1. Update Excel File

Edit: `config/finance/Month-end Closing Task and Tax Filing (7).xlsx`

### 2. Run Generator Script

```bash
python3 addons/ipai_finance_ppm_umbrella/scripts/generate_seed_from_excel.py
```

**Output**:
```
🚀 Generating Canonical Seed Data from Excel

📂 Source: config/finance/Month-end Closing Task and Tax Filing (7).xlsx
📂 Output: addons/ipai_finance_ppm_umbrella/data

✅ Generated: addons/ipai_finance_ppm_umbrella/data/01_employees.xml
✅ Generated: addons/ipai_finance_ppm_umbrella/data/02_logframe_complete.xml
✅ Generated: addons/ipai_finance_ppm_umbrella/data/03_bir_schedule.xml
✅ Generated: addons/ipai_finance_ppm_umbrella/data/04_closing_tasks.xml
```

### 3. Reload Module

```bash
odoo -d production -u ipai_finance_ppm_umbrella
```

## Testing

### Manual Testing

1. **Access Finance PPM Menu** in Odoo
2. **Navigate to**:
   - Logframe entries
   - BIR Schedule
   - Month-End Closing Tasks
3. **Verify**:
   - All records loaded
   - Employee assignments correct
   - RACI matrix populated
   - Deadlines calculated correctly

### Automated Testing

```sql
-- Test 1: Employee count
SELECT
  CASE
    WHEN COUNT(*) = 8 THEN '✅ PASS'
    ELSE '❌ FAIL'
  END AS result,
  COUNT(*) AS actual,
  8 AS expected
FROM res_users
WHERE login IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb');

-- Test 2: Logframe structure
SELECT
  level,
  COUNT(*) AS count
FROM ipai_finance_logframe
GROUP BY level
ORDER BY level;

-- Test 3: BIR schedule per employee
SELECT
  supervisor_id,
  COUNT(*) AS bir_forms
FROM ipai_finance_bir_schedule
GROUP BY supervisor_id;

-- Test 4: Closing task categories
SELECT
  description,
  COUNT(*) AS tasks
FROM project_task
WHERE finance_logframe_id IS NOT NULL
GROUP BY description;
```

## Troubleshooting

### Issue: Module installation fails

**Solution**: Ensure base `ipai_finance_ppm` module is installed first.

```bash
odoo -d production -i ipai_finance_ppm
odoo -d production -i ipai_finance_ppm_umbrella
```

### Issue: Seed data not loading

**Symptom**: Empty tables after installation

**Solution**: Check Odoo logs for XML parsing errors:

```bash
# Check for noupdate flag
grep "noupdate" addons/ipai_finance_ppm_umbrella/data/*.xml

# Force reload with update
odoo -d production -u ipai_finance_ppm_umbrella --log-level=debug
```

### Issue: RACI assignments missing

**Symptom**: Supervisor/reviewer/approver fields empty

**Solution**: Verify employee user records exist:

```sql
SELECT id, name, login
FROM res_users
WHERE login IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb');
```

If missing, check `01_employees.xml` loaded correctly.

### Issue: Generator script fails

**Symptom**: Excel file not found

**Solution**: Verify paths and run from project root:

```bash
# Check Excel file exists
ls -lh config/finance/Month-end\ Closing\ Task\ and\ Tax\ Filing\ \(7\).xlsx

# Run from project root
cd /path/to/project-root
python3 addons/ipai_finance_ppm_umbrella/scripts/generate_seed_from_excel.py
```

## Integration with Finance SSC Workflows

### Month-End Closing Workflow

1. **Week 1-3**: Execute closing tasks (36 tasks)
   - Assigned to employees per RACI matrix
   - Tracked via `project.task` with logframe links

2. **Week 4**: BIR form preparation
   - Prep deadline: BIR - 4 business days
   - Assigned to Finance Supervisor (BOM)

3. **Week 4+1**: Review and approval
   - Review: Senior Finance Manager (RIM)
   - Approval: Finance Director (CKVC)

4. **BIR Deadline**: File and remit
   - Status updated to "filed"
   - Completion percentage = 100%

### Reporting and Dashboards

**Finance PPM Dashboard** displays:
- BIR deadline timeline (bar chart)
- Completion tracking (percentage bar chart)
- Status distribution (pie chart)
- Logframe task count overview

**Access**: `/ipai/finance/ppm`

## License

LGPL-3

## Author

InsightPulse AI

## Version History

- **1.0.0** (2025-12-26): Initial release with 8 employees, 144 BIR forms, 36 closing tasks

## Support

For issues or questions, contact: Finance SSC Team (TBWA)
