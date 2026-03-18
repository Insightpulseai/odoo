# ipai_advisor

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Azure Advisor-style recommendations engine for operational governance

## Dependencies

- `base`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 5 |
| Views | 11 |
| Menus | 8 |
| Actions | 6 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_advisor --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_advisor --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.321685_
