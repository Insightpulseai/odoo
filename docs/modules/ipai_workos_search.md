# ipai_workos_search

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Global and scoped search for pages and databases

## Dependencies

- `base`
- `web`
- `ipai_workos_core`
- `ipai_workos_blocks`
- `ipai_workos_db`

## Module Contents

| Type | Count |
|------|-------|
| Models | 2 |
| Views | 1 |
| Menus | 1 |
| Actions | 1 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_workos_search --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_workos_search --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.926340_
