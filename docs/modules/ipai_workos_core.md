# ipai_workos_core

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Notion-style Work OS - Core module with workspaces, spaces, and pages

## Dependencies

- `base`
- `web`
- `mail`
- `ipai_platform_permissions`
- `ipai_platform_audit`

## Module Contents

| Type | Count |
|------|-------|
| Models | 3 |
| Views | 10 |
| Menus | 5 |
| Actions | 3 |
| Data Files | 5 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_workos_core --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_workos_core --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.902402_
