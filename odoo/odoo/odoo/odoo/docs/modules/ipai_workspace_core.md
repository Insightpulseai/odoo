# ipai_workspace_core

**Status**: ✅ PASS
**Version**: 18.0.1.0.1
**Author**: InsightPulse AI

## Summary

Unified workspace model for marketing agencies and accounting firms.

## Dependencies

- `ipai_dev_studio_base`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 7 |
| Menus | 2 |
| Actions | 2 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_workspace_core --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_workspace_core --stop-after-init
```

---
_Audited: 2026-01-21T22:42:54.957907_
