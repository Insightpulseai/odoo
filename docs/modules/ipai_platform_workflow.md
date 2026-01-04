# ipai_platform_workflow

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: IPAI

## Summary

Generic workflow state machine for IPAI modules

## Dependencies

- `base`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 0 |
| Menus | 0 |
| Actions | 0 |
| Data Files | 2 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_platform_workflow --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_platform_workflow --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.668972_
