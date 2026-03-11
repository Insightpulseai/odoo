# ipai_master_control

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Bridge Odoo events to Master Control work items

## Dependencies

- `base`
- `hr`
- `hr_expense`
- `purchase`

## Module Contents

| Type | Count |
|------|-------|
| Models | 4 |
| Views | 0 |
| Menus | 0 |
| Actions | 0 |
| Data Files | 2 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_master_control --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_master_control --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.878157_
