# ipai_finance_bir_compliance

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

JSON-seeded BIR schedule that generates Prep/Review/Approval/Filing tasks into IM2

## Dependencies

- `project`
- `mail`
- `ipai_project_program`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 4 |
| Menus | 3 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_bir_compliance --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_bir_compliance --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.324333_
