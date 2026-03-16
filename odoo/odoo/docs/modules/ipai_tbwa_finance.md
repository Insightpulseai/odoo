# ipai_tbwa_finance

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: IPAI / TBWA

## Summary

Unified month-end closing + BIR tax compliance for TBWA Philippines

## Dependencies

- `base`
- `mail`
- `account`

## Module Contents

| Type | Count |
|------|-------|
| Models | 8 |
| Views | 18 |
| Menus | 9 |
| Actions | 6 |
| Data Files | 13 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_tbwa_finance --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_tbwa_finance --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.603212_
