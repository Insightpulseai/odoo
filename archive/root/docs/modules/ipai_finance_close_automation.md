# ipai_finance_close_automation

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Month-end close generator with working-day deadline offsets

## Dependencies

- `project`
- `resource`
- `ipai_finance_close_seed`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 1 |
| Menus | 2 |
| Actions | 1 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_finance_close_automation --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_finance_close_automation --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.333971_
