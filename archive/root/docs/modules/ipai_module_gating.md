# ipai_module_gating

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Automated production readiness assessment and install/upgrade gating for Odoo modules

## Dependencies

- `base`

## Module Contents

| Type | Count |
|------|-------|
| Models | 1 |
| Views | 3 |
| Menus | 3 |
| Actions | 5 |
| Data Files | 4 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_module_gating --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_module_gating --stop-after-init
```

---
_Audited: 2026-01-21T22:42:53.938089_
