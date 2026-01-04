# ipai_grid_view

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: IPAI Team

## Summary

Advanced grid and list view with sorting, filtering, and bulk actions

## Dependencies

- `base`
- `web`
- `mail`

## Module Contents

| Type | Count |
|------|-------|
| Models | 8 |
| Views | 9 |
| Menus | 4 |
| Actions | 3 |
| Data Files | 6 |

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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_grid_view --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_grid_view --stop-after-init
```

---
_Audited: 2026-01-04T10:26:06.562163_
