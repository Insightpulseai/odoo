# ipai_finance_ppm_tdi

**Status**: ✅ PASS
**Version**: 1.0.0
**Author**: InsightPulse AI - Jake Tolentino

## Summary

Import finance team, tasks, BIR calendar, and LogFrame data

## Dependencies

- `base`
- `project`
- `hr`
- `account`

## Module Contents

| Type | Count |
|------|-------|
| Models | 4 |
| Views | 4 |
| Menus | 5 |
| Actions | 2 |
| Data Files | 10 |

## Validation Results

| Check | Status |
|-------|--------|
| Manifest | ✅ |
| Python Syntax | ✅ |
| XML Syntax | ✅ |
| Security CSV | ✅ |
| Init Imports | ✅ |

## Install/Upgrade

```bash
# Install
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_ppm_tdi --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_ppm_tdi --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.493467_
