# ipai_tbwa_finance

## Overview

**Technical Name**: `ipai_tbwa_finance`
**Summary**: Unified month-end closing + BIR tax compliance for TBWA Philippines
**Version**: 18.0.1.0.0
**License**: AGPL-3
**Author**: IPAI / TBWA

## Dependencies

### Odoo Core Modules
- `base`
- `mail`
- `account`

### IPAI Modules
None

## Data Model

### Python Models
- `models/closing_period.py`
- `models/finance_task_template.py`
- `models/compliance_check.py`
- `models/ph_holiday.py`
- `models/bir_return.py`
- `models/finance_task.py`
- `models/res_partner.py`

## Automation

### Scheduled Actions (Cron Jobs)
- **TBWA Finance: Send Overdue Notifications** (`cron_overdue_notifications`)
  - File: `data/ir_cron.xml`

## Configuration

### Data Files
- `data/ph_holidays.xml`
- `data/compliance_checks.xml`
- `data/ir_cron.xml`
- `data/bir_form_types.xml`
- `data/month_end_templates.xml`

## Odoo 18 Compatibility

### Known Issues
✅ No known compatibility issues

### Migration Notes
- Odoo 18 removes the `ir.cron.numbercall` field
- Cron jobs now run indefinitely by default (equivalent to `numbercall=-1`)
- The `nextcall`, `interval_number`, and `interval_type` fields remain supported

## Verification

### Installation Check
```sql
SELECT name, state, latest_version
FROM ir_module_module
WHERE name = 'ipai_tbwa_finance';
-- Expected: state='installed'
```

### Cron Job Check
```sql
SELECT name, active, nextcall, interval_number, interval_type
FROM ir_cron
WHERE model = 'finance.task'
  AND active = true;
-- Expected: 1 active cron job
```
