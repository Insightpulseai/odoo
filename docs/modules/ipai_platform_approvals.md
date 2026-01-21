# ipai_platform_approvals

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: IPAI

## Summary

Role-based approval chains for IPAI modules

## Dependencies

- `base`
- `mail`
- `ipai_platform_workflow`

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_platform_approvals --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_platform_approvals --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.070989_
