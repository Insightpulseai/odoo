# ipai_expense

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

PH-focused expense & travel workflows (SAP Concur-style) on Odoo CE + OCA.

## Dependencies

- `hr`
- `hr_expense`
- `account`
- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 7 |
| Menus | 2 |
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

- ⚠️ Subpackages not imported in __init__.py: ['tests']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_expense --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_expense --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.254287_
