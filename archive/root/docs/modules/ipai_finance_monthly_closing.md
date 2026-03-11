# ipai_finance_monthly_closing

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Structured month-end closing and BIR filing on top of Projects (CE/OCA-only).

## Dependencies

- `project`

## Module Contents

| Type | Count |
|------|-------|
| Models | 1 |
| Views | 0 |
| Menus | 0 |
| Actions | 0 |
| Data Files | 3 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_monthly_closing --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_monthly_closing --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.416396_
