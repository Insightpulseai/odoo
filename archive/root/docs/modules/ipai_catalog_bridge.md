# ipai_catalog_bridge

**Status**: ✅ PASS
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## Summary

Unity Catalog-like asset registry bridge for Odoo ↔ Supabase sync

## Dependencies

- `base`
- `mail`
- `ipai_dev_studio_base`

## Module Contents

| Type | Count |
|------|-------|
| Models | 6 |
| Views | 6 |
| Menus | 3 |
| Actions | 2 |
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
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -i ipai_catalog_bridge --stop-after-init

# Upgrade
odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_catalog_bridge --stop-after-init
```

---
_Audited: 2026-01-21T22:42:52.851590_
