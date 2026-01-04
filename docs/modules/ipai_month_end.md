# ipai_month_end

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: IPAI

## Summary

SAP AFC replacement - Month-end closing automation

## Dependencies

- `base`
- `mail`
- `account`

## Module Contents

| Type | Count |
|------|-------|
| Models | 4 |
| Views | 15 |
| Menus | 6 |
| Actions | 4 |
| Data Files | 9 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_month_end --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_month_end --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.605256_
