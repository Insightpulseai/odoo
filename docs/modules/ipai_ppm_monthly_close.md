# ipai_ppm_monthly_close

**Status**: ⚠️ WARN
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Automated monthly financial close scheduling with PPM and Notion workspace parity

## Dependencies

- `base`
- `project`
- `mail`
- `resource`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 8 |
| Menus | 4 |
| Actions | 4 |
| Data Files | 7 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_ppm_monthly_close --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_ppm_monthly_close --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.723365_
