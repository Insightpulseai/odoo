# Finance PPM Generator Contract v1.2.0

## Overview

Seed JSON files that define **hierarchical task templates** for Finance PPM workflows with:
- **Deterministic external keys** for idempotent upsert
- **Recurrence rules** for monthly/quarterly/annual cycles
- **Completeness validation** (PASS/WARN/FAIL)
- **Assignment resolution** via employee codes

---

## Architecture

### Data Flow

```
Seed JSON → Validator → Template Storage → Instance Generator → Odoo Tasks
```

### Database Tables (3)

1. **`ipai_close_task_template`** - Template storage with hierarchical metadata
2. **`ipai_close_generation_run`** - Audit trail for each generator execution
3. **`ipai_close_generated_map`** - External key → `project_task.id` mapping (deduplication)

### Custom Fields on `project_task` (6)

- `x_cycle_key` - Instance identifier: `MONTH_END_CLOSE|2025-10`
- `x_task_template_code` - Template slug: `CT_PAYROLL_PROCESSING`
- `x_step_code` - Step identifier: `PREP|REVIEW|APPROVAL`
- `x_external_key` - Full deduplication key (see format below)
- `x_seed_hash` - SHA256 hash for change detection
- `x_obsolete` - Boolean flag for removed templates

---

## External Key Format (Canonical)

**Format**: `<cycle_key>|<phase_code>|<workstream_code>|<category_code>|<template_code>|<step_code>`

**Example**:
```
MONTH_END_CLOSE|2025-10|II_ACCRUALS|AMORTIZATION|CT_IT_FIXED_ASSETS_AMORT|PREP
```

**Components**:
- `cycle_key` - Computed from recurrence + period: `MONTH_END_CLOSE|2025-10`
- `phase_code` - Phase identifier: `I_INITIAL_COMPLIANCE`
- `workstream_code` - Workstream slug: `PAYROLL`
- `category_code` - Category slug: `PAYROLL_PERSONNEL`
- `template_code` - Template slug (stable): `CT_PAYROLL_PROCESSING`
- `step_code` - Step type: `PREP`, `REVIEW`, `APPROVAL`, `FILE_PAY`

**Uniqueness**: This key must be **globally unique** across all cycles, phases, and periods.

---

## Hierarchy

```
Cycle (e.g., MONTH_END_CLOSE)
 └─ Phase (e.g., I_INITIAL_COMPLIANCE)
     └─ Workstream (e.g., PAYROLL)
         └─ Category (e.g., PAYROLL_PERSONNEL)
             └─ Task Template (e.g., CT_PAYROLL_PROCESSING)
                 └─ Steps (PREP, REVIEW, APPROVAL)
```

**Levels**:
1. **Cycle** - Recurring process type (monthly/quarterly/annual)
2. **Phase** - Major milestone group (I Initial, II Accruals, etc.)
3. **Workstream** - Functional area (Payroll, IT, Recons)
4. **Category** - Sub-grouping within workstream (Payroll Personnel, IT Fixed Assets)
5. **Task Template** - Specific deliverable (Process Payroll, Amortize IT Assets)
6. **Steps** - Execution stages (Prep → Review → Approval)

---

## Recurrence Rules

### Monthly Cycles

**Cycle Key**: `MONTH_END_CLOSE|YYYY-MM`

**Anchor**: Last day of month (`MONTH_END`)

**Example**:
```json
{
  "cycle_code": "MONTH_END_CLOSE",
  "recurrence": { "freq": "MONTHLY" },
  "anchor": { "type": "MONTH_END" }
}
```

**Generated Instances**:
- `MONTH_END_CLOSE|2025-10` (Oct 31, 2025)
- `MONTH_END_CLOSE|2025-11` (Nov 30, 2025)
- `MONTH_END_CLOSE|2025-12` (Dec 31, 2025)

### Quarterly Cycles (Tax Filing)

**Cycle Key**: `TAX_FILING_QUARTERLY|YYYY-QN`

**Anchor**: BIR deadline for quarter

**Example**:
```json
{
  "cycle_code": "TAX_FILING_QUARTERLY",
  "recurrence": { "freq": "QUARTERLY" },
  "anchor": { "type": "BIR_DEADLINE", "form": "2550Q" }
}
```

**Generated Instances**:
- `TAX_FILING_QUARTERLY|2025-Q4` (deadline: 2026-02-28)
- `TAX_FILING_QUARTERLY|2026-Q1` (deadline: 2026-05-31)

### Monthly Tax Filing

**Cycle Key**: `TAX_FILING_MONTHLY|YYYY-MM`

**Anchor**: BIR deadline (10th of following month for 1601-C, 0619-E)

**Example**:
```json
{
  "cycle_code": "TAX_FILING_MONTHLY",
  "bir_form_code": "1601-C",
  "recurrence": { "freq": "MONTHLY" },
  "anchor": { "type": "BIR_DEADLINE", "day": 10, "offset_months": 1 }
}
```

---

## Due Date Calculation

### Offset from Anchor

**Business Days** (default):
```json
{
  "due": {
    "offset_business_days": -6
  }
}
```

**Calendar Days**:
```json
{
  "due": {
    "offset_calendar_days": -10
  }
}
```

### Absolute Dates (Override)

```json
{
  "due": {
    "absolute_date": "2025-10-25"
  }
}
```

### Computation Logic

For anchor = Oct 31, 2025 (MONTH_END):
- `offset_business_days: -6` → Oct 23, 2025 (6 business days before)
- `offset_business_days: -3` → Oct 28, 2025 (3 business days before)
- `offset_business_days: 0` → Oct 31, 2025 (anchor date)

---

## Assignment Resolution

### Employee Code Mapping

**Field**: `res.users.x_employee_code`

**Strategy**: Lookup user by employee code from seed JSON

**Example Mapping**:
```json
{
  "assignee_employee_code": "RIM",
  "role": "preparer"
}
```

**Resolution**:
```python
user = env['res.users'].search([('x_employee_code', '=', 'RIM')], limit=1)
task.user_ids = [(4, user.id)]  # Assign to task
```

**Standard Employee Codes**:
- `RIM` - Rey Meran (Senior Finance Manager / Preparer)
- `CKVC` - Khalil Veracruz (Finance Director / Approver)
- `BOM` - Beng Manalo (Finance Supervisor / Reviewer)
- `LAS` - Amor Lasaga (Financial Analyst)
- `RMQB` - Sally Brillantes (Finance Clerk)
- `JPAL` - Jerald Loterte (AP/AR Specialist)
- `JLI` - Jasmin Ignacio (Tax Compliance)
- `JAP` - Jinky Paladin (GL Accountant)

---

## Completeness Validation

### FAIL (Hard Errors - Block Execution)

- Missing `cycle_code`, `phase_code`, `workstream_code`, `category_code`
- Missing `template_code` or `name`
- No steps defined (`steps: []`)
- Step missing `step_code`
- Step missing `assignee_employee_code`
- Step missing `due` offset or absolute date

### WARN (Soft Errors - Allow with Warnings)

- `assignee_employee_code` doesn't resolve to user (task left unassigned)
- Duration values missing (computed from step offsets)
- Recurrence rule malformed (skip instance generation)
- Anchor date can't be computed (use fallback)

### PASS (Valid)

- All required fields present
- All employee codes resolve to users
- Durations match step offsets
- Recurrence expands successfully

**Validation Report Format**:
```json
{
  "status": "PASS|WARN|FAIL",
  "errors": ["Critical error 1", "Critical error 2"],
  "warnings": ["Warning 1", "Warning 2"]
}
```

---

## Seed JSON Schema

### Top-Level Structure

```json
{
  "version": "1.2.0",
  "seed_id": "ipai_finance_ppm_closing",
  "defaults": {
    "timezone": "Asia/Manila",
    "uom_days": "business_days",
    "assign_resolution": {
      "strategy": "employee_code",
      "field": "res.users.x_employee_code"
    }
  },
  "cycles": [ /* cycle definitions */ ]
}
```

### Cycle Definition

```json
{
  "cycle_code": "MONTH_END_CLOSE",
  "name": "Month-End Closing",
  "description": "Monthly financial close process",
  "recurrence": {
    "freq": "MONTHLY"
  },
  "anchor": {
    "type": "MONTH_END"
  },
  "phases": [ /* phase definitions */ ]
}
```

### Phase Definition

```json
{
  "phase_code": "I_INITIAL_COMPLIANCE",
  "name": "Initial & Compliance",
  "sequence": 10,
  "description": "Payroll, statutory compliance, initial recons",
  "workstreams": [ /* workstream definitions */ ]
}
```

### Workstream Definition

```json
{
  "workstream_code": "PAYROLL",
  "name": "Payroll Processing & Tax Provision",
  "sequence": 10,
  "categories": [ /* category definitions */ ]
}
```

### Category Definition (NEW in v1.2.0)

```json
{
  "category_code": "PAYROLL_PERSONNEL",
  "name": "Payroll & Personnel",
  "sequence": 10,
  "task_templates": [ /* task template definitions */ ]
}
```

### Task Template Definition

```json
{
  "template_code": "CT_PAYROLL_PROCESSING",
  "name": "Process and record Payroll, Final Pay, SL Conversions, early retirement accrual",
  "description": "Complete payroll processing with all statutory deductions",
  "wbs_code_template": "PP-{period}",
  "critical_path": false,
  "duration": {
    "prep_days": 1,
    "review_days": 0.5,
    "approval_days": 0.5
  },
  "steps": [ /* step definitions */ ]
}
```

### Step Definition

```json
{
  "step_code": "PREP",
  "name_template": "Prepare Payroll Processing for {period}",
  "role": "preparer",
  "assignee_employee_code": "RIM",
  "due": {
    "offset_business_days": -6
  },
  "duration_days": 1,
  "dependencies": []
}
```

---

## Mapping from Excel Sheet to Seed JSON

### Column Mapping

| Excel Column | JSON Path | Example |
|--------------|-----------|---------|
| Phase | `cycles[].phases[].phase_code` | `I_INITIAL_COMPLIANCE` |
| Workstream | `phases[].workstreams[].workstream_code` | `PAYROLL` |
| Task Category | `workstreams[].categories[].category_code` | `PAYROLL_PERSONNEL` |
| Task Details | `categories[].task_templates[].name` | "Process Payroll..." |
| Prep (Assignee) | `task_templates[].steps[0].assignee_employee_code` | `RIM` |
| Review (Assignee) | `task_templates[].steps[1].assignee_employee_code` | `RIM` |
| Approval (Assignee) | `task_templates[].steps[2].assignee_employee_code` | `CKVC` |
| Due Days Before | `steps[].due.offset_business_days` | `-6` (6 days before close) |

### BIR Schedule Mapping

| Excel Column | JSON Path | Example |
|--------------|-----------|---------|
| BIR Form | `bir_form_code` | `1601-C` |
| Covered Period | `period_covered` | `2025-10` |
| Deadline | `anchor.absolute_date` | `2025-11-10` |
| Process Steps | `steps[]` | Prep/Report Approval/Payment Approval/File & Pay |

---

## Generator Usage

### Dry Run (Validation Only)

```python
env = odoo.api.Environment(cr, uid, {})
generator = env['ipai.close.generator']

report = generator.generate_tasks_from_seed(
    seed_json_path='addons/ipai_finance_ppm/seed/closing_v1_2_0.json',
    cycle_key='MONTH_END_CLOSE|2025-10',
    period_start='2025-10-01',
    period_end='2025-10-31',
    project_id=30,
    dry_run=True  # No database writes
)

print(report)
# {
#   "status": "PASS",
#   "created": 45,
#   "updated": 0,
#   "obsolete": 0,
#   "warnings": [],
#   "errors": []
# }
```

### Apply (Create Tasks)

```python
report = generator.generate_tasks_from_seed(
    seed_json_path='addons/ipai_finance_ppm/seed/closing_v1_2_0.json',
    cycle_key='MONTH_END_CLOSE|2025-10',
    period_start='2025-10-01',
    period_end='2025-10-31',
    project_id=30,
    dry_run=False  # Write to database
)
```

### Subsequent Runs (Idempotent)

```python
# Same command - will only update if seed JSON changed (via SHA256 hash)
report = generator.generate_tasks_from_seed(
    seed_json_path='addons/ipai_finance_ppm/seed/closing_v1_2_0.json',
    cycle_key='MONTH_END_CLOSE|2025-10',
    period_start='2025-10-01',
    period_end='2025-10-31',
    project_id=30,
    dry_run=False
)

# Result: {"status": "PASS", "created": 0, "updated": 0, "skipped": 45}
```

### Obsolete Task Detection

```python
# If you remove a task template from seed JSON and re-run:
report = generator.generate_tasks_from_seed(
    seed_json_path='addons/ipai_finance_ppm/seed/closing_v1_2_1.json',  # Updated version
    cycle_key='MONTH_END_CLOSE|2025-10',
    period_start='2025-10-01',
    period_end='2025-10-31',
    project_id=30,
    dry_run=False
)

# Result: {"status": "PASS", "created": 0, "updated": 0, "obsolete": 5}
# Tasks no longer in seed JSON are marked with x_obsolete=True
```

---

## Files in This Directory

- **`closing_v1_2_0.json`** - Complete month-end closing seed (all phases, all workstreams)
- **`tax_filing_v1_2_0.json`** - BIR tax filing seed (1601-C, 2550Q, 1702-RT, etc.)
- **`README.md`** - This file (contract specification)

---

## Version History

### v1.2.0 (2025-11-22)
- Added **category** hierarchy layer between workstream and task template
- Changed external key format to include category_code
- Added recurrence expansion logic for monthly/quarterly/annual cycles
- Added completeness validation (PASS/WARN/FAIL)
- Split closing and tax filing into separate seed files

### v1.0.0 (2025-11-15)
- Initial generator contract
- Basic hierarchy: cycle → phase → workstream → task_template → steps
- Idempotent upsert via external_key
- SHA256 hash-based change detection
