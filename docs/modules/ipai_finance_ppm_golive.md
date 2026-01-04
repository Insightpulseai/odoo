# ipai_finance_ppm_golive

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Production go-live checklist for Finance PPM modules

## Dependencies

- `base`
- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 7 |
| Menus | 6 |
| Actions | 5 |
| Data Files | 9 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ Subpackages not imported in __init__.py: ['reports']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_ppm_golive --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_ppm_golive --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.478606_
