# ipai_finance_ppm

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

Finance Project Portfolio Management (Notion Parity).

## Dependencies

- `base`
- `mail`
- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 17 |
| Views | 24 |
| Menus | 12 |
| Actions | 11 |
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

- ⚠️ Subpackages not imported in __init__.py: ['controllers']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_ppm --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_ppm --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.392826_
