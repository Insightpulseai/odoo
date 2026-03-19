# ipai_approvals

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulseAI

## Summary

Generic approval workflow system - Enterprise Approvals parity for Odoo CE

## Dependencies

- `base`
- `mail`
- `hr`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 9 |
| Menus | 6 |
| Actions | 5 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_approvals --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_approvals --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.621182_
