# ipai_workos_templates

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Page and database templates

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
| Views | 3 |
| Menus | 1 |
| Actions | 1 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_workos_templates --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_workos_templates --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.935066_
