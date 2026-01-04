# ipai_equipment

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

Cheqroom-style equipment catalog, bookings, and incidents on Odoo CE + OCA.

## Dependencies

- `stock`
- `maintenance`
- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 15 |
| Menus | 5 |
| Actions | 4 |
| Data Files | 3 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_equipment --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_equipment --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.300550_
