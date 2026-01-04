# ipai_finance_project_hybrid

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

Turns finance phases into IM projects, seeds finance directory/BIR schedule, generates month-end + compliance tasks, and adds analytics dashboards.

## Dependencies

- `project`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 7 |
| Views | 12 |
| Menus | 7 |
| Actions | 5 |
| Data Files | 11 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_project_hybrid --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_project_hybrid --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.539433_
