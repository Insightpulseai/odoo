# ipai_finance_ppm_closing

**Status**: ⚠️ WARN
**Version**: 18.0.1.1.0
**Author**: InsightPulseAI

## Summary

Idempotent Month-End Close & BIR Task Generator with audit trail.

## Dependencies

- `project`
- `ipai_finance_ppm`
- `ipai_ppm_monthly_close`

## Module Contents

| Type | Count |
|------|-------|
| Models | 6 |
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

- ⚠️ Subpackages not imported in __init__.py: ['tests', 'scripts']

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_ppm_closing --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_ppm_closing --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.451197_
