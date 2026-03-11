# ipai_finance_closing

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Month-end financial closing task template based on SAP Advanced Financial Closing

## Dependencies

- `project`
- `account`

## Module Contents

| Type | Count |
|------|-------|
| Models | 0 |
| Views | 0 |
| Menus | 0 |
| Actions | 3 |
| Data Files | 1 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_closing --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_closing --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.373150_
