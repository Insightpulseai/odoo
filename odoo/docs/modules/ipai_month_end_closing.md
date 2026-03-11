# ipai_month_end_closing

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

SAP AFC-style month-end closing with BIR tax compliance for TBWA Finance

## Dependencies

- `project`
- `hr`

## Module Contents

| Type | Count |
|------|-------|
| Models | 0 |
| Views | 0 |
| Menus | 9 |
| Actions | 5 |
| Data Files | 5 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_month_end_closing --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_month_end_closing --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.982306_
