# ipai_tenant_core

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Multi-tenant platform core for InsightPulse AI

## Dependencies

- `base`
- `mail`
- `web`

## Module Contents

| Type | Count |
|------|-------|
| Models | 1 |
| Views | 3 |
| Menus | 2 |
| Actions | 1 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_tenant_core --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_tenant_core --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.637709_
