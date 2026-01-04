# ipai_finance_month_end

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

JSON-seeded month-end templates that generate Preparation/Review/Approval tasks into IM1

## Dependencies

- `project`
- `mail`
- `ipai_project_program`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 4 |
| Menus | 4 |
| Actions | 2 |
| Data Files | 5 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ Subpackages not imported in __init__.py: ['tests', 'seed']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_month_end --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_month_end --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.366292_
