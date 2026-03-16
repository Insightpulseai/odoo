# ipai_finance_ppm

**Status**: ⚠️ WARN
**Version**: 18.0.1.1.0
**Author**: InsightPulse AI

## Summary

Finance Project Portfolio Management (Notion Parity).

## Dependencies

- `base`
- `mail`
- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 19 |
| Views | 29 |
| Menus | 16 |
| Actions | 15 |
| Data Files | 18 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ⚠️ |

## Warnings

- ⚠️ Subpackages not imported in __init__.py: ['tests', 'controllers']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_ppm --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_ppm --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.429940_
